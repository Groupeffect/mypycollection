import os
from pprint import pprint
import rdflib as r


class OntologyLoader:

    def __init__(self, path) -> None:
        self.graph = r.Graph()
        self.graph.parse(path)
        print(path)


class Mixin:
    resultFolderPath = "./results"

    def save(self, text, format="xml"):
        with open(f'{self.resultFolderPath}/{self.name}.{format}', 'w') as f:
            f.write(text)
            f.close()

    def info(self, rdfClass, graph=None):
        if not graph:
            graph = self.graph
        return{
            "objects": [*graph.objects(subject=rdfClass)],
            "subjects": [*graph.subjects(predicate=rdfClass)],
            "subject_objects": [*graph.subject_objects(predicate=rdfClass)],
            "subject_predicates": [(*i, rdfClass) for i in graph.subject_predicates(object=rdfClass)],
            "predicates": [*self.graph.predicates(subject=rdfClass)],
            "predicate_objects": [(rdfClass, *i) for i in graph.predicate_objects(subject=rdfClass)],
        }


class Load(Mixin):
    def __init__(
        self, name='SDO', saveFile=False, includeParentClasses=False,
        assetsFolderPath='./assets', resultFolderPath='./result',
    ) -> None:
        self.name = name
        self.graph = None
        self.saveFile = saveFile
        self.includeParentClasses = includeParentClasses
        self.resultFolderPath = resultFolderPath
        self.assetsFolderPath = assetsFolderPath

        if name.lower() in ['sdo']:
            self.graph = OntologyLoader(
                path=f'{self.assetsFolderPath}/schemaorg-current-https.rdf').graph

    def test(self):
        result = self.partial().serialize(format="xml")
        # result = self.simple(r.SDO.Organization).serialize(format="xml")
        if self.saveFile:
            self.save(result, 'rdf')

        # pprint(self.info(r.SDO.Project))
        # pprint(self.simple(r.SDO.Project).serialize(format="xml"))

    def search(self, rdfClass=None, triple=None):
        result = r.Graph()
        if triple:
            [result.add(i) for i in self.graph.triples(triple)]
            return result

        [result.add(i) for i in self.graph.triples((rdfClass, None, None))]
        [result.add(i) for i in self.graph.triples((None, rdfClass, None))]
        [result.add(i) for i in self.graph.triples((None, None, rdfClass))]
        return result

    def simple(self, rdfClass):
        info = self.info(rdfClass=rdfClass)
        result = r.Graph()
        for i in [*info['predicate_objects'], *info['subject_predicates']]:
            result.add(i)
        return result

    def partial(self, classes=[
            r.SDO.Organization,
            r.SDO.Project,
            r.SDO.Person,
            # r.SDO.ImageObject,
            # r.SDO.Time,
            # r.SDO.Date,
            # r.SDO.Place,
            # r.SDO.Text,
            # r.SDO.Number,
            # r.SDO.Boolean,
        ],
    ):
        result = r.Graph()

        for c in classes:
            result += self.search(c)
            if self.includeParentClasses:
                for parent in self.search(triple=(c, r.RDFS.subClassOf, None)).triples((None, None, None)):
                    result += self.search(rdfClass=parent[2])

            for subClass in [*result.triples((c, r.RDFS.subClassOf, None)), [None, None, c]]:
                info = self.info(subClass[2])
                for predicate in info['subject_predicates']:
                    # result += self.search(triple=(predicate[0],
                    #                               None, None))
                    result += self.search(triple=(predicate[0],
                                                  r.RDFS.comment, None))
                    result += self.search(triple=(predicate[0],
                                                  r.RDF.type, None))
                    result += self.search(triple=(predicate[0],
                                                  r.OWL.equivalentClass, None))
                    result += self.search(triple=(predicate[0],
                                                  r.RDFS.label, None))

        return result


class MetaApplication(Mixin):
    def __init__(self, category="backend", domainUri="https://localhost:8000/") -> None:
        self.category = category
        self.domainUri = domainUri
        self.name = "backend"

        self.standards = [r.SDO.Person, r.SDO.Organization,
                          r.SDO.BankAccount, r.SDO.Project]
        self.graph = self.get_ontology()

    def uri(self, name):
        return r.URIRef(f'{self.domainUri}{name}')

    def create_class(self, label, comment="test comment", parentClass=None):
        classInstance = self.uri(label)
        graph = r.Graph()
        if parentClass:
            graph.add((classInstance, r.RDFS.subClassOf, parentClass))
            graph.add((parentClass, r.RDF.type, r.RDFS.Class))
        graph.add((classInstance, r.RDF.type, r.RDFS.Class))
        graph.add((classInstance, r.RDFS.label, r.Literal(label)))
        graph.add((classInstance, r.RDFS.comment, r.Literal(comment)))
        return graph

    def add_standard(self, rdfClasses, graph):
        for rdfClass in rdfClasses:
            graph.add(
                (
                    rdfClass,
                    r.RDFS.label,
                    r.Literal(str(rdfClass).split('/')[-1])
                )
            )
            graph.add((rdfClass, r.RDF.type, r.RDFS.Class))
        return graph

    def set_relations(self, graph):
        account = self.uri('Account')
        user = self.uri('User')
        self.add_standard(self.standards, graph)
        graph.add((account, r.SDO.domainIncludes, user))
        graph.add((account, r.SDO.domainIncludes, r.SDO.Organization))  # noqa
        graph.add((account, r.SDO.domainIncludes, r.SDO.Project))  # noqa
        graph.add((user, r.SDO.memberOf, r.SDO.Project))  # noqa
        graph.add((user, r.SDO.memberOf, r.SDO.Project))  # noqa
        graph.add((user, r.SDO.memberOf, r.SDO.Organization))  # noqa
        graph.add((r.SDO.Organization, r.SDO.ownedFrom, user))  # noqa
        graph.add((account, r.SDO.ownedFrom, user))  # noqa
        return graph

    def get_ontology(self):
        result = r.Graph()
        if self.category in ['backend', 'django']:
            result += self.create_class('User', parentClass=r.SDO.Person)
            result += self.create_class('Account',
                                        parentClass=r.SDO.BankAccount)
            result = self.set_relations(result)

            # result += Load().partial()
        return result

    def test(self):
        pprint(self.graph.serialize(format='xml'))
        pprint(self.info(self.uri('User')))
        self.save(format='rdf', text=self.graph.serialize(format='xml'))


if __name__ == "__main__":

    # result = Load(
    #     name='partial_sdo',
    #     saveFile=True,
    #     includeParentClasses=True
    # ).test()

    result = MetaApplication().test()
