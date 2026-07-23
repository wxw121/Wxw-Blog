# -*- coding: utf-8 -*-
import re
from _articles_128_136_content import article_128
from _articles_128_136_content_part2 import (
    article_129, article_130, article_131, article_132,
    article_133, article_134, article_135, article_136,
)
from _articles_128_136_expand import EXPANSIONS
from _articles_128_136_expand2 import EXPANSIONS2

def hc(t):
    return len(re.findall(r"[\u4e00-\u9fff]", t))

articles = {
    "langchain-vectorstore": article_128(),
    "langchain-document-loader": article_129(),
    "langchain-text-splitter": article_130(),
    "llamaindex-index-types": article_131(),
    "llamaindex-query-engine": article_132(),
    "llamaindex-agent": article_133(),
    "haystack-pipeline": article_134(),
    "pipeline-vs-framework": article_135(),
    "pluggable-parser-splitter-embedder": article_136(),
}
for slug, text in articles.items():
    if isinstance(text, tuple):
        text = text[0]
    total = text + EXPANSIONS.get(slug, "") + EXPANSIONS2.get(slug, "")
    print(f"{slug}: base={hc(text)} e1={hc(EXPANSIONS.get(slug,''))} e2={hc(EXPANSIONS2.get(slug,''))} total={hc(total)}")
