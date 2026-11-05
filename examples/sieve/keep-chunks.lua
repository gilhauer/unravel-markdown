-- Copyright (C) 2026 Gil Hauer
-- SPDX-License-Identifier: GPL-3.0-only
-- See LICENSE in the project root for the full license text.

-- Keep each short chunk heading with its code when printing this example.
function Blocks(blocks)
  if FORMAT ~= "typst" then
    return nil
  end

  local result = pandoc.List()
  local i = 1
  while i <= #blocks do
    local current, following = blocks[i], blocks[i + 1]
    if current.t == "Header" and current.level == 3
      and pandoc.utils.stringify(current):match("^<<")
      and following and following.t == "CodeBlock" then
      result:insert(pandoc.RawBlock("typst", "#block(breakable: false)["))
      result:insert(current)
      result:insert(following)
      result:insert(pandoc.RawBlock("typst", "]"))
      i = i + 2
    else
      result:insert(current)
      i = i + 1
    end
  end
  return result
end
