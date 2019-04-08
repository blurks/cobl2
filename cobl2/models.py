from __future__ import unicode_literals

import sqlalchemy as sa
import sqlalchemy.orm

from clld.db.meta import CustomModelMixin, Base
from clld.db.models.common import Parameter, Language, Contribution, Contributor, Value, Identifier, IdentifierType
from clld.lib.color import is_bright
from clld_cognacy_plugin.models import MeaningMixin, Cognateset


class Lexeme(CustomModelMixin, Value):
    pk = sa.Column(sa.Integer, sa.ForeignKey('value.pk'), primary_key=True)
    native_script = sa.Column(sa.Unicode)
    phonetic = sa.Column(sa.Unicode)
    phonemic = sa.Column(sa.Unicode)
    comment = sa.Column(sa.Unicode)
    gloss = sa.Column(sa.Unicode)
    url = sa.Column(sa.Unicode)


class Meaning(CustomModelMixin, Parameter, MeaningMixin):
    pk = sa.Column(sa.Integer, sa.ForeignKey('parameter.pk'), primary_key=True)
    example_context = sa.Column(sa.Unicode)
    wiki = sa.Column(sa.Unicode)
    count_languages = sa.Column(sa.Integer)
    count_cognateclasses = sa.Column(sa.Integer)
    count_loan_cognateclasses = sa.Column(sa.Integer)
    count_lexemes = sa.Column(sa.Integer)


class CognateClass(CustomModelMixin, Cognateset):
    pk = sa.Column(sa.Integer, sa.ForeignKey('cognateset.pk'), primary_key=True)
    root_form = sa.Column(sa.Unicode)
    root_form_calc = sa.Column(sa.Unicode)
    root_gloss = sa.Column(sa.Unicode)
    root_language = sa.Column(sa.Unicode)
    root_language_calc = sa.Column(sa.Unicode)
    source = sa.Column(sa.Unicode, default=None)
    meaning_pk = sa.Column(sa.Integer, sa.ForeignKey('meaning.pk'))
    meaning = sa.orm.relationship(Meaning, backref='cognateclasses')
    color = sa.Column(sa.Unicode)

    loan_source_pk = sa.Column(sa.Integer, sa.ForeignKey('cognateclass.pk'))
    loan_notes = sa.Column(sa.Unicode)
    loan_source_form = sa.Column(sa.Unicode)
    loan_source_languoid = sa.Column(sa.Unicode)
    parallel_loan_event = sa.Column(sa.Boolean, default=False)
    ideophonic = sa.Column(sa.Boolean, default=False)
    is_loan = sa.Column(sa.Boolean, default=False)
    comment = sa.Column(sa.Unicode)
    justification = sa.Column(sa.Unicode)
    count_lexemes = sa.Column(sa.Integer)
    count_clades = sa.Column(sa.Integer)
    loans = sa.orm.relationship(
        'CognateClass',
        foreign_keys=[loan_source_pk],
        backref=sa.orm.backref('loan_source', remote_side=[pk]))

    meaning_rel = sa.orm.relationship('Meaning', viewonly=True)

    def __unicode__(self):
        if self.root_form:
            res = self.root_form
        elif self.root_form_calc:
            res = self.root_form_calc
        if self.root_language:
            res += ' [{0}]'.format(self.root_language)
        elif self.root_language_calc:
            res += ' [{0}]'.format(self.root_language_calc)
        if len(res) > 0:
            return res
        return Cognateset.__unicode__(self)


class Variety(CustomModelMixin, Language):
    pk = sa.Column(sa.Integer, sa.ForeignKey('language.pk'), primary_key=True)
    contribution_pk = sa.Column(sa.Integer, sa.ForeignKey('contribution.pk'))
    contribution = sa.orm.relationship(
        Contribution, backref=sa.orm.backref('variety', uselist=False))
    color = sa.Column(sa.Unicode)
    clade = sa.Column(sa.Unicode)
    clade_name = sa.Column(sa.Unicode)
    fossil = sa.Column(sa.Boolean, default=False)
    historical = sa.Column(sa.Boolean, default=False)
    glottocode = sa.Column(sa.Unicode)
    ascii_name = sa.Column(sa.Unicode)
    iso = sa.Column(sa.Unicode)
    earliest_time_depth_bound = sa.Column(sa.Integer)
    latest_time_depth_bound = sa.Column(sa.Integer)
    lang_description = sa.Column(sa.Unicode)
    variety = sa.Column(sa.Unicode)
    sort_order = sa.Column(sa.Integer)

    @property
    def fontcolor(self):
        return '#000' if is_bright(self.color) else '#eee'

    def get_identifier_objs(self, type_):
        o = Identifier()
        if getattr(type_, 'value', type_) == str(IdentifierType.glottolog):
            if not self.glottocode: return []
            o.name = self.glottocode
            o.type = str(IdentifierType.glottolog)
            return [o]
        if getattr(type_, 'value', type_) == str(IdentifierType.iso):
            if not self.iso: return []
            o.name = self.iso
            o.type = str(IdentifierType.iso)
            return [o]
        return []


class Author(CustomModelMixin, Contributor):
    pk = sa.Column(sa.Integer, sa.ForeignKey('contributor.pk'), primary_key=True)
    photo = sa.Column(sa.String)
