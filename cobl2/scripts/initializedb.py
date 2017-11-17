from __future__ import unicode_literals
import sys

from clld.scripts.util import initializedb, Data
from clld.db.meta import DBSession
from clld.db.models import common
from clld.lib.bibtex import EntryType
from clldutils.misc import slug
from clldutils.path import Path, read_text
from nameparser import HumanName
from pycldf import Wordlist

import cobl2
from cobl2 import models
import clld_cognacy_plugin.models

ds = Wordlist.from_metadata(
    Path(cobl2.__file__).parent / '../..' / 'cobl-data' / 'cldf' / 'Wordlist-metadata.json')
wiki = Path(cobl2.__file__).parent / '../..' / 'CoBL-public.wiki'


def get_contributor(data, name):
    name = HumanName(name.strip())
    id_ = slug(name.last + name.first)
    res = data['Contributor'].get(id_)
    if not res:
        res = data.add(common.Contributor, id_, id=id_, name=name.original)
    return res


def main(args):
    data = Data()

    dataset = common.Dataset(
        id=cobl2.__name__,
        name="CoBL-IE",
        publisher_name="Max Planck Institute for the Science of Human History",
        publisher_place="Jena",
        publisher_url="http://www.shh.mpg.de",
        license="http://creativecommons.org/licenses/by/4.0/",
        domain='cobl2.clld.org',
        jsondata={
            'license_icon': 'cc-by.png',
            'license_name': 'Creative Commons Attribution 4.0 International License'})

    DBSession.add(dataset)
    for i, ed in enumerate(['Paul Heggarty', 'Cormac Anderson']):
        common.Editor(dataset=dataset, contributor=get_contributor(data, ed), ord=i + 1)

    for src in ds.sources.items():
        for invalid in ['isbn', 'part', 'institution']:
            if invalid in src:
                del src[invalid]
        data.add(
            common.Source,
            src.id,
            id=src.id,
            name=src.get('author', src.get('editor')),
            description=src.get('title', src.get('booktitle')),
            bibtex_type=getattr(EntryType, src.genre, EntryType.misc),
            **src)

    def clean_md(t):
        lines = []
        for line in t.splitlines():
            if line.startswith('#'):
                line = '##' + line
            lines.append(line)
        return '\n'.join(lines)

    for param in ds['ParameterTable']:
        wiki_page = wiki / '{0}.md'.format(param['Name'])
        data.add(
            models.Meaning,
            param['ID'],
            id=param['ID'],
            name=param['Name'],
            description=param['Description'],
            wiki=clean_md(read_text(wiki_page)) if wiki_page.exists() else None,
            example_context=param['Example_Context'],
            concepticon_id=int(param['Conceptset']) if param['Conceptset'] != '0' else None,
        )

    for row in ds['LanguageTable']:
        c = data.add(
            common.Contribution,
            row['ID'],
            id=row['ID'],
            name='{0} Dataset'.format(row['Name']),
        )
        for i, author in enumerate(row['Authors']):
            contrib = get_contributor(data, author)
            DBSession.add(common.ContributionContributor(
                contribution=c, contributor=contrib, ord=i + 1))
        data.add(
            models.Variety,
            row['ID'],
            id=row['ID'],
            name=row['Name'],
            latitude=float(row['Latitude']),
            longitude=float(row['Longitude']),
            contribution=c,
        )

    for row in ds['FormTable']:
        vs = data['ValueSet'].get((row['Language_ID'], row['Parameter_ID']))
        if not vs:
            vs = data.add(
                common.ValueSet,
                (row['Language_ID'], row['Parameter_ID']),
                id='{0}-{1}'.format(row['Language_ID'], row['Parameter_ID']),
                language=data['Variety'][row['Language_ID']],
                parameter=data['Meaning'][row['Parameter_ID']],
                contribution=data['Contribution'][row['Language_ID']],
            )
        v = data.add(
            common.Value,
            row['ID'],
            id=row['ID'],
            name=row['Romanised'],
            valueset=vs
        )
        for src in row['Source']:
            sid, pages = ds.sources.parse(src)
            DBSession.add(common.ValueSetReference(
                valueset=vs, source=data['Source'][sid], description=pages))

    for row in ds['CognatesetTable']:
        data.add(
            models.CognateClass,
            row['ID'],
            id=row['ID'],
            name=row['ID'],
            root_form=row['Root_Form'],
            root_gloss=row['Root_Gloss'],
            root_language=row['Root_Language'],
        )

    for row in ds['CognateTable']:
        data.add(
            clld_cognacy_plugin.models.Cognate,
            row['ID'],
            cognateset=data['CognateClass'][row['Cognateset_ID']],
            counterpart=data['Value'][row['Form_ID']],
        )


def prime_cache(args):
    """If data needs to be denormalized for lookup, do that here.
    This procedure should be separate from the db initialization, because
    it will have to be run periodically whenever data has been updated.
    """


if __name__ == '__main__':
    initializedb(create=main, prime_cache=prime_cache)
    sys.exit(0)
