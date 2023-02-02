import bz2
import json
from pathlib import Path

from rdflib import RDFS, Graph, Literal, Namespace
from tqdm import tqdm


def wikidata(filename, progress_label="Wikidata"):
    filename = str(filename)
    with bz2.open(filename, mode="rt") as file_obj:
        with tqdm(desc=progress_label, total=1523565366625) as pbar:
            file_obj.read(2)  # skip first two bytes: "{\n"
            pbar.update(2)
            for line in file_obj:
                try:
                    yield json.loads(line.rstrip(",\n"))
                except json.decoder.JSONDecodeError:
                    continue
                finally:
                    pbar.update(len(line))


WD = Namespace("http://www.wikidata.org/entity/")
WDT = Namespace("http://www.wikidata.org/prop/direct/")


def main(entity_type, *props):

    find_next = set()

    for entity in wikidata(
        "latest-all.json.bz2", progress_label=f"Finding entities of type {entity_type}"
    ):
        if "P31" not in entity["claims"]:
            continue

        entity_types = [
            snak["mainsnak"]["datavalue"]["value"]["id"]
            for snak in entity["claims"]["P31"]
            if "datavalue" in snak["mainsnak"]
        ]
        if entity_type not in entity_types:
            continue

        g = Graph()
        g.add(
            (
                WD[entity["id"]],
                WDT["P31"],
                WD[entity_type],
            )
        )

        if "en" not in entity["labels"]:
            continue

        g.add(
            (
                WD[entity["id"]],
                RDFS.label,
                Literal(entity["labels"]["en"]["value"]),
            )
        )

        for prop in props:
            if prop in entity["claims"]:
                for claim in entity["claims"][prop]:
                    snak = claim["mainsnak"]
                    if "datavalue" in snak:
                        if snak["datatype"] == "wikibase-item":
                            g.add(
                                (
                                    WD[entity["id"]],
                                    WDT[prop],
                                    WD[snak["datavalue"]["value"]["id"]],
                                )
                            )
                            find_next.add(snak["datavalue"]["value"]["id"])
                        else:
                            g.add(
                                (
                                    WD[entity["id"]],
                                    WDT[prop],
                                    Literal(snak["datavalue"]["value"]),
                                )
                            )

        print(g.serialize(format="nt"))

    for entity in wikidata(
        Path.home() / "latest-all.json.bz2",
        progress_label=f"Looking for linked entities",
    ):
        if entity["id"] in find_next and "en" in entity["labels"]:
            g = Graph()
            g.add(
                (
                    WD[entity["id"]],
                    RDFS.label,
                    Literal(entity["labels"]["en"]["value"]),
                )
            )
            print(g.serialize(format="nt"))


if __name__ == "__main__":
    main("Q11424", "P345", "P57", "P136", "P921", "P161")
