---
layout: post
title: "Logic Tensor Networks: the Smokes–Friends–Cancer example"
date: 2026-08-18 09:00:00+0100
description: A hands-on walkthrough of the canonical Logic Tensor Networks example, showing how first-order logic axioms become a differentiable, trainable neural model.
tags: neuro-symbolic-ai logic-tensor-networks jupyter machine-learning
categories: neuro-symbolic
giscus_comments: false
related_posts: false
---

The [Logic Tensor Networks](https://github.com/logictensornetworks/logictensornetworks) (LTN) framework
bridges symbolic reasoning and deep learning: you write down domain knowledge as **first-order logic
axioms**, and the model learns tensor groundings that **satisfy** those axioms as well as possible.

This notebook works through the canonical LTN example — a small social network where we know who smokes,
who is friends with whom, and (partially) who has cancer. Along the way it explains the ideas that make
LTN tick:

- how symbols (people, predicates) are *grounded* as tensors and neural networks,
- how fuzzy connectives replace Boolean logic,
- how `Forall` and `Exists` become **fold (reduce) operations** over truth-value tensors,
- and the LTN training loop: maximise satisfaction ↔ minimise `1 - sat`.

The notebook interleaves the working code with short Q&A boxes answering the questions that naturally
come up the first time you read LTN code (why embedding size 10? which fuzzy algebra? where do the
`p` values come from?).

{::nomarkdown}
{% assign jupyter_path = 'assets/jupyter/01_smokes_friends_cancer.ipynb' | relative_url %}
{% capture notebook_exists %}{% file_exists assets/jupyter/01_smokes_friends_cancer.ipynb %}{% endcapture %}
{% if notebook_exists == 'true' %}
{% jupyter_notebook jupyter_path %}
{% else %}
<p>Sorry, the notebook you are looking for does not exist.</p>
{% endif %}
{:/nomarkdown}
