
# Module: <code>netlink.attributes</code>
Implements netlink attribute parsing.

<code>**class** [Policy](#policy)</code><br>
<span class="docs">An attribute policy returned by a netlink request.</span>

## Attribute Types
`NL_ATTR_TYPE_INVALID = 0`<br>
`NL_ATTR_TYPE_FLAG = 1`<br>
`NL_ATTR_TYPE_U8 = 2`<br>
`NL_ATTR_TYPE_U16 = 3`<br>
`NL_ATTR_TYPE_U32 = 4`<br>
`NL_ATTR_TYPE_U64 = 5`<br>
`NL_ATTR_TYPE_S8 = 6`<br>
`NL_ATTR_TYPE_S16 = 7`<br>
`NL_ATTR_TYPE_S32 = 8`<br>
`NL_ATTR_TYPE_S64 = 9`<br>
`NL_ATTR_TYPE_BINARY = 10`<br>
`NL_ATTR_TYPE_STRING = 11`<br>
`NL_ATTR_TYPE_NUL_STRING = 12`<br>
`NL_ATTR_TYPE_NESTED = 13`<br>
`NL_ATTR_TYPE_NESTED_ARRAY = 14`<br>
`NL_ATTR_TYPE_BITFIELD32 = 15`

## Policy
`type: int`<br>
`policy_id: int | None`<br>
`policy_maxtype: int | None`<br>
`min_length: int | None`<br>
`max_length: int | None`<br>
`min_value: int | None`<br>
`max_value: int | None`<br>
`mask: int | None`
