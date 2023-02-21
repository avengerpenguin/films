import bz2
import json
from pathlib import Path

import pydash
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


def main():
    for entity in wikidata(
        Path.home() / "latest-all.json.bz2", progress_label=f"Wikidata"
    ):
        label = pydash.get(entity, "labels.en.value")
        if not label:
            continue

        g = Graph()
        g.add(
            (
                WD[entity["id"]],
                RDFS.label,
                Literal(label),
            )
        )

        for prop, snaks in entity["claims"].items():
            prop_uri = WDT[prop]
            for snak in snaks:
                match pydash.get(snak, "mainsnak.datavalue.type"):
                    case "string":
                        g.add(
                            (
                                WD[entity["id"]],
                                prop_uri,
                                Literal(pydash.get(snak, "mainsnak.datavalue.value")),
                            )
                        )
                    case "wikibase-entityid":
                        g.add(
                            (
                                WD[entity["id"]],
                                prop_uri,
                                WD[pydash.get(snak, "mainsnak.datavalue.value.id")],
                            )
                        )

        print(g.serialize(format="nt"))


if __name__ == "__main__":
    main()
