---
layout: post
title: "Part 2: Logic Tensor Networks: grounding and variables"
date: 2026-08-23 09:00:00+0100
read_time: 26 # minutes; set explicitly because the embedded notebook is not counted by the listing's word-count formula
description: The second LTN tutorial — how constants, variables, predicates and functions become tensors, and why variable broadcasting is the key to writing your own axioms.
tags: neuro-symbolic-ai logic-tensor-networks jupyter machine-learning
categories: neuro-symbolic
giscus_comments: false
related_posts: false
---

This is the second notebook in the [Logic Tensor Networks](https://github.com/logictensornetworks/logictensornetworks)
(LTN) series. The [first post]({% post_url 2026-08-18-logic-tensor-networks-smokes-friends-cancer %})
used `ltn.Constant`, `ltn.Variable` and `ltn.Predicate.MLP` without looking closely at the tensors they
produce. This one fixes that — and understanding the shapes is essential before you can write your own
axioms.

**What you will see:**

- the four kinds of LTN symbols: constants, variables, predicates, and functions,
- two ways to define a predicate — a `Lambda` for a fixed formula vs a custom Keras model when you need
  learnable weights,
- what an `ltn.Function` is and how it differs from a predicate,
- **variable broadcasting**: why `P(x, y)` with `|x|=10`, `|y|=5` produces a `(10, 5)` tensor,
- the `free_vars` attribute that tracks which tensor axis belongs to which variable,
- and how quantifiers collapse those axes — connecting back to the *fold* idea from the first post.

As before, the working code is interleaved with short Q&A boxes answering the questions that come up the
first time you read LTN code (Lambda vs MLP? why a `(10, 5)` tensor and not `(50,)`? what is a
`GradientTape` and why must variables be rebuilt inside it?).

{::nomarkdown}
{% assign jupyter_path = 'assets/jupyter/02_grounding_and_variables.ipynb' | relative_url %}
{% capture notebook_exists %}{% file_exists assets/jupyter/02_grounding_and_variables.ipynb %}{% endcapture %}
{% if notebook_exists == 'true' %}
{% jupyter_notebook jupyter_path %}
{% else %}
<p>Sorry, the notebook you are looking for does not exist.</p>
{% endif %}
{:/nomarkdown}
