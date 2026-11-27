-- pandoc filter: keep the cover on its own page (the HTML marks it with class "page")
local pagebreak = pandoc.RawBlock('openxml', '<w:p><w:r><w:br w:type="page"/></w:r></w:p>')
function Div(el)
  if el.classes:includes('page') then
    el.content:insert(pagebreak)
    return el
  end
end

-- drop the HTML <title> so pandoc does not add a second title above the cover heading
function Meta(m)
  m.title = nil
  return m
end
