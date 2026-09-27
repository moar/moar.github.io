---
layout: post
title: "Visual Sudoku: pure deep learning vs a neuro-symbolic approach"
date: 2026-09-27 09:00:00+0100
read_time: 61 # minutes; set explicitly because the two embedded notebooks are not counted by the listing's word-count formula
description: Reproducing the ViSudo-PC benchmark two ways — a purely CNN-based classifier vs a Logic Tensor Network that learns digits from puzzle-validity labels alone — and comparing what each one buys you.
tags: neuro-symbolic-ai logic-tensor-networks jupyter machine-learning computer-vision
categories: neuro-symbolic
giscus_comments: false
related_posts: false
---

The earlier posts in this series built up Logic Tensor Networks from the ground up, the
[Smokes–Friends–Cancer example]({% post_url 2026-08-18-logic-tensor-networks-smokes-friends-cancer %}),
[grounding and variables]({% post_url 2026-08-23-logic-tensor-networks-grounding-and-variables %}), and a
full [knowledge base with learning]({% post_url 2026-08-28-logic-tensor-networks-knowledge-base-and-learning %}).
This post puts the framework to work on a harder, genuinely perceptual problem named **Visual Sudoku**. We will use it to understand which can be the advantage of using symbolic knowledge over a straight deep-learning baseline.

## The task: ViSudo-PC

The problem comes from the **ViSudo-PC** benchmark (Augustine et al., *Visual Sudoku Puzzle
Classification*) and the LTN reproduction by Morra et al. (["Solving Visual Sudoku with Logic Tensor
Networks"](https://ceur-ws.org/Vol-3432/paper19.pdf)). Instead of a Sudoku of typed numbers, each cell is
an **image** drawn from MNIST (and, in harder variants, EMNIST / FashionMNIST / KMNIST). The system is
shown a full board and must answer a single yes/no question: **is this a valid Sudoku?**, i.e. does every
row, column, and block contain each symbol exactly once, with no repetitions?

What makes it a good neuro-symbolic testbed is that it needs *both* kinds of reasoning at once:

- **perceptual** — recognise the digit in each of the 16 (4×4) or 81 (9×9) cell images, and
- **collective/symbolic**  reason over all cells together against the Sudoku constraints.

We use the simplest variant throughout — **MNIST, 4×4** and compare two ways of solving it.

## Approach 1 — pure deep learning (CNN baseline)

The straightforward supervised route: train a CNN on individual cell images with **digit-level labels**,
read off the predicted digit for every cell, and then check the Sudoku rules symbolically on the predicted
grid. Cell-level accuracy is very high, but a single misread cell can
flip the whole board's label.

{::nomarkdown}
{% assign jupyter_path_1 = 'assets/jupyter/sudoku_part1_cnn_baseline.ipynb' | relative_url %}
{% capture nb1_exists %}{% file_exists assets/jupyter/sudoku_part1_cnn_baseline.ipynb %}{% endcapture %}
{% if nb1_exists == 'true' %}
{% jupyter_notebook jupyter_path_1 %}
{% else %}
<p>Sorry, the notebook you are looking for does not exist.</p>
{% endif %}
{:/nomarkdown}

## Approach 2: neuro-symbolic implementation with Logic Tensor Networks

The neuro-symbolic route flips the supervision around. Following the *indirect solution* of Morra et al.,
the CNN is trained **from scratch with no digit labels at all**. The only supervision is the puzzle-level
valid/invalid flag. The Sudoku rules, written as first-order logic axioms, provide the entire training
signal: the network is pushed to assign digits so that valid puzzles satisfy the constraints and invalid
ones violate them. The notebook below walks through the domains, variables, predicates and the two axioms
that make this work.

{::nomarkdown}
{% assign jupyter_path_2 = 'assets/jupyter/sudoku_part2_symbolic.ipynb' | relative_url %}
{% capture nb2_exists %}{% file_exists assets/jupyter/sudoku_part2_symbolic.ipynb %}{% endcapture %}
{% if nb2_exists == 'true' %}
{% jupyter_notebook jupyter_path_2 %}
{% else %}
<p>Sorry, the notebook you are looking for does not exist.</p>
{% endif %}
{:/nomarkdown}

## Results & comparison

| Metric (MNIST 4×4) | Pure DL (CNN baseline) | Neuro-symbolic (LTN, indirect #1) |
|---|---|---|
| Digit-level supervision | Yes — every cell labelled | **No** — none |
| Labels required | A digit label on every cell | One validity flag per puzzle (valid/invalid) |
| Training signal | Supervised digit classification (cross-entropy) | Logic-axiom satisfaction (`loss = 1 − sat`) |
| Cell-level accuracy | *(from mlruns)* | — |
| Puzzle-level accuracy | **851 / 900 = 0.946** | **815 / 900 = 0.906** |

The headline result: the LTN reaches **≈90.6% puzzle-level accuracy** on the 4×4 MNIST boards *without ever
seeing a single digit label* — just **4 points** below the fully-supervised CNN baseline's **94.6%**. It is
told only whether each whole puzzle is valid or not; the Sudoku rules, encoded as first-order logic axioms,
supply the rest of the training signal and force the CNN to discover the digits on its own.

That is the core neuro-symbolic payoff: **symbolic knowledge substitutes for dense supervision.** For a ~4-point
accuracy drop, the LTN removes the per-cell labelling requirement entirely: the baseline needs a label on
every one of the 16 cells, while the LTN needs just one bit per board. When cell-level annotation is expensive
or unavailable but the *rules* of the domain are known, that trade is often well worth making.

