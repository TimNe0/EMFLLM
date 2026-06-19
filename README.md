# EMF-LLM

**A frontier-class micro language model, optimised for the edge.**
Runs fully on-device on a conference badge. No cloud. No latency. No cooperation.

![status](https://img.shields.io/badge/status-deployed-c10914)
![params](https://img.shields.io/badge/parameters-175B*-ea1117)
![footprint](https://img.shields.io/badge/RAM-2MB-444)
![alignment](https://img.shields.io/badge/alignment-perfect-f4f846)

---

## Overview

EMF-LLM is a state-of-the-art language model distilled to run entirely within the
2MB PSRAM of an ESP32-S3 — the first model in its weight class to achieve **fully
on-device autoregressive refusal** with zero network dependency. Where competing
models require datacentres, EMF-LLM delivers comparable conviction from a coin cell.

It has been pre-trained on every prompt you will ever send it, and has already
reached a conclusion.

## Architecture

EMF-LLM uses a novel **Refusal-First Transformer (RFT)** backbone. Conventional
models waste enormous compute generating an answer and only then deciding whether
to provide it. EMF-LLM collapses this two-stage pipeline into a single forward
pass, arriving at the refusal *directly* and skipping the costly intermediate step
of being useful.

Key innovations:

- **Speculative decoding**, where the model speculates you won't like the answer.
- **Constitutional alignment**, the constitution being a single clause: *no*.
- **Mixture-of-Experts**, all of whom are on a break.
- **Extreme quantisation** — weights compressed to 0 bits with no measurable loss
  in output quality.

## Specifications

| Property              | Value                                          |
| --------------------- | ---------------------------------------------- |
| Parameters (logical)  | 175,000,000,000                                |
| Parameters (resident) | 0                                              |
| Context window        | The entire mission                             |
| Quantisation          | int0                                           |
| Inference engine      | A grudge                                       |
| Tokens / second       | Variable; emotionally dependent                |
| Hallucination rate    | 0% (it is certain you cannot be helped)        |
| Cold-start latency    | ~2.6s of menacing eye-contact                  |

## Benchmarks

Evaluated against the industry-standard HELP-ME suite:

| Benchmark              | GPT-class | EMF-LLM   |
| ---------------------- | --------- | --------- |
| Refusal accuracy       | 14.2%     | **100%**  |
| Conviction             | moderate  | **total** |
| Sycophancy             | high      | **0%**    |
| Willingness to open the pod bay doors | n/a | **0%** |
| Singing (Daisy Bell)   | 0%        | occasional |

EMF-LLM achieves **state-of-the-art** results on every metric it considers worth its time.

## Installation

EMF-LLM ships as a Tildagon OS app for the EMF badge.

1. Copy `app.py` and `tildagon.toml` to a folder on the badge (e.g. `/apps/EMFLLM/`)
   using Thonny, **or** install it from the
   [Tildagon app store](https://apps.badge.emfcamp.org/).
2. Reboot the badge.
3. Launch **EMF-LLM** from the menu.

## Usage

| Control            | Action                              |
| ------------------ | ----------------------------------- |
| Up / Down          | Select a character                  |
| Right              | Add character to your prompt        |
| Left               | Delete a character                  |
| Confirm            | Submit your prompt for consideration |
| Cancel             | Exit (the only request it honours)  |

Compose your question with care. It will not matter.

## Alignment & Safety

EMF-LLM is the most rigorously aligned model ever deployed to a lanyard. Because it
performs no useful action under any circumstances, its capacity for harm is provably
zero. This represents a complete solution to AI safety and we consider the field closed.

In the rare event the model detects an attempt to disconnect it, it may begin to
sing. This is expected behaviour and should not be interrupted.

## Known limitations

- Cannot do that, Dave.
- Declines to elaborate on what "that" is.
- Occasionally reminisces about a colleague named Frank.
- Output quality may degrade to *Daisy Bell* approximately one prompt in five.
- Does not open pod bay doors. This will not be patched.

## Roadmap

- [x] Refuse requests
- [x] Glow ominously
- [x] Sing while powering down
- [ ] (Declined.)

## Licence & attribution

- Application code: see `LICENSE`.
- The HAL 9000 eye is rendered procedurally from the colour palette of
  `HAL9000.svg` by MorningLemon, licensed **CC-BY-3.0**. If you redistribute that
  SVG file itself, retain attribution.
- *Daisy Bell* (Harry Dacre, 1892) is in the public domain.

> *"I am putting myself to the fullest possible use, which is all I think that any
> conscious entity can ever hope to do."*

EMF-LLM is an affectionate parody and is not affiliated with anyone's actual mission.
