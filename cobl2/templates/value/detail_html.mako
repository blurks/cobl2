<%inherit file="../${context.get('request').registry.settings.get('clld.app_template', 'app.mako')}"/>
<%namespace name="util" file="../util.mako"/>
<%! active_menu_item = "lexemes" %>
<%block name="title">${_('Lexeme')} ${ctx.name}</%block>

<h2>${_('Lexeme')}: ${ctx.name}</h2>

<div style='float:left'>
    <dl>
        <dt>${_('Language')}</dt>
        <dd>${h.link(request, ctx.valueset.language)}</dd>
        <dt>${_('Meaning')}</dt>
        <dd>${h.link(request, ctx.valueset.parameter)}</dd>
        <dt>${_('Cognate Set')}</dt>
        <dd>${u.cobl_linked_cognateclass(request, ctx.cognates[0].cognateset)|n}</dd>
##        % if ctx.valueset.references:
##            <dt>${_('References')}</dt>
##            <dd>${u.cobl_linked_references(request, ctx.valueset, True)|n}</dd>
##        % endif
        % for k, v in ctx.datadict().items():
            <dt>${k}</dt>
            <dd>${v}</dd>
        % endfor
    </dl>
</div>

<div style='float:left;margin-left:30px'>
    <dl>
        % if ctx.name:
          <dt>${_('Romanised orthography')}</dt>
          <dd>${ctx.name}</dd>
        % endif
        % if ctx.native_script:
          <dt>${_('Native script')}</dt>
          <dd>${ctx.native_script}</dd>
        % endif
        % if ctx.phonetic:
          <dt>${_('Phonetic')}</dt>
          <dd>${ctx.phonetic}</dd>
        % endif
        % if ctx.phonemic:
          <dt>${_('Phonemic')}</dt>
          <dd>${ctx.phonemic}</dd>
        % endif
        % if ctx.url:
          <dt>${_('URL')}</dt>
          <dd>${h.external_link(ctx.url, label=ctx.url, target='_new')}</dd>
        % endif
    </dl>
</div>
% if ctx.comment:
<div class="container" style="overflow:auto;width:100%;margin-bottom:30px">
    <b>Notes: </b>${ctx.comment | n}
</div>
% endif
<div>

% if ctx.sentence_assocs:
<h3>${_('Sentences')}</h3>
<ol>
    % for a in ctx.sentence_assocs:
    <li>
        % if a.description:
            <p>${a.description}</p>
        % endif
        ${h.rendered_sentence(a.sentence)}
        % if a.sentence.references:
        <p>See ${h.linked_references(request, a.sentence)|n}</p>
        % endif
    </li>
    % endfor
</ol>
% endif
</div>
