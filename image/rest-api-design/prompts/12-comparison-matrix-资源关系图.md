---
layout: comparison-matrix
style: hand-drawn-edu
aspect: 16:9
language: zh
---

Educational infographic in hand-drawn-edu style: warm cream paper background (#F5F0E8), macaron pastel rounded cards
(mint #B5E5CF, blue #A8D8EA, lavender #D5C6E0, peach #FFD5C2), hand-drawn wobble lines,
stick-figure characters, doodle decorations, Chinese text labels, landscape 16:9, generous whitespace.
Layout: Table or matrix comparison layout
All visible text in Chinese (简体中文).
Content to visualize faithfully:
                        资源关系图

    /articles                     /users
    ├── GET  (列表)               ├── POST    (注册)
    ├── POST (创建)               ├── GET     (列表——管理员)
    │                             │
    ├── /articles/{id}            ├── /users/{id}
    │   ├── GET    (详情)         │   ├── GET    (资料)
    │   ├── PUT    (更新)         │   ├── PATCH  (修改资料)
    │   ├── DELETE (删除)         │   ├── DELETE (注销——管理员)
    │   │                         │   │
    │   ├── /articles/{id}/comments   ├── /users/{id}/articles
    │   │   ├── GET    (列表)     │   │   └── GET (该用户的文章)
    │   │   └── POST   (创建)     │   │
    │   │                         │   └── /users/{id}/favorites
    │   └── /articles/{id}/favorite   │   ├── GET    (收藏列表)
    │       ├── POST   (收藏)     │   └── DELETE (取消收藏)
    │       └── DELETE (取消收藏)  │
    │                             │
    └── /articles/{id}/comments/{commentId}
        ├── GET    (单个评论)
        ├── PUT    (更新评论)
        └── DELETE (删除评论)