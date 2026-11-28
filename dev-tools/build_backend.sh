#!/bin/bash
# Build a Node-runnable copy of the edge function (in-memory DB)
SRC="$1"
sed -e 's#^import postgres from "npm:postgres@3.4.4";#const postgres=()=>null;#' -e 's#^Deno\.serve(#globalThis.__serve=(#' "$SRC" > backend.mjs
echo 'globalThis.handleKartuKu=handleKartuKu;' >> backend.mjs
