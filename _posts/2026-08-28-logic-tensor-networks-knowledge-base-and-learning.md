---
layout: post
title: "Part 3: Logic Tensor Networks: knowledge base and learning"
date: 2026-08-28 09:00:00+0100
read_time: 27 # minutes; set explicitly because the embedded notebook is not counted by the listing's word-count formula
description: The third LTN tutorial — building a complete knowledge base and training a semi-supervised classifier that labels 19 points from just two labels and one rule.
tags: neuro-symbolic-ai logic-tensor-networks jupyter machine-learning
categories: neuro-symbolic
giscus_comments: false
related_posts: false
---

This is the third notebook in the [Logic Tensor Networks](https://github.com/logictensornetworks/logictensornetworks)
(LTN) series. The first two posts introduced the
[Smokes–Friends–Cancer example]({% post_url 2026-08-18-logic-tensor-networks-smokes-friends-cancer %})
and looked closely at [grounding and variables]({% post_url 2026-08-23-logic-tensor-networks-grounding-and-variables %}).
Here we put the pieces together into a complete learning system: a **knowledge base** of axioms, a
training loop that maximises satisfaction, and a visualisation of what the model learned.

**The problem:** It's a semisupervised problem where we have 19 points. Only two are labelled: one class A, one class B. The rest are
unlabelled. We know just two things: A and B are mutually exclusive, and nearby points share the same
class. Can the model classify every point from those two labels and those two rules alone? As we only have 2D, this problem could be of course easily solved with a KNN classifier. Howeverk, keep in mind that
that in this example 
1) we are injecting symbolic rules. KNN only interpolates from data. LTN lets you add logical constraints that have no data equivalent (e.g. "cancer implies smokes OR has-family-history", "a doctor cannot also be a patient"). These constraints actively shape the learned representation.
2) The rules are readable and auditable. The KB is written in first-order logic. A domain expert can inspect, add, or challenge rules without touching the neural architecture. KNN has no such interface.
3) Semi-supervised scales differently. KNN needs labelled neighbours and in high-dimensional sparse spaces it degrades badly. LTN can propagate labels through logical rules even when geometric proximity breaks down.
4) You learn embeddings, not just boundaries. LTN trains the predicate MLP weights — the model learns a representation. KNN is non-parametric; it memorises data points. When the domain has structure a neural representation can exploit (language, images, graphs), LTN can leverage that.

**What is new here compared to the earlier notebooks:**

- a predicate `C(x, l)` that takes **both a data point and a class label** as inputs,
- a **softmax** output that bakes mutual exclusivity between classes into the architecture,
- the `Equiv` (↔) connective, and why it is built from your chosen `And` and `Implies` rather than being
  a primitive,
- the `@tf.function` decorator,  what graph compilation buys you and why the KB must be run once before
  training,
- and the pattern for **batched training** when the dataset is too large to fit in a single tensor.

As in the rest of the series, the working code is interleaved with short Q&A boxes answering the
questions that come up on a first read (why a label input? softmax vs sigmoid? what does `@tf.function`
actually do?).

{::nomarkdown}
{% assign jupyter_path = 'assets/jupyter/03_kb_and_learning.ipynb' | relative_url %}
{% capture notebook_exists %}{% file_exists assets/jupyter/03_kb_and_learning.ipynb %}{% endcapture %}
{% if notebook_exists == 'true' %}
{% jupyter_notebook jupyter_path %}
{% else %}
<p>Sorry, the notebook you are looking for does not exist.</p>
{% endif %}
{:/nomarkdown}
