"""System Design: one module per topic, in the order they appear on the site.
Topics reuse the Deep Dive block schema (content/deepdive/_blocks.py) and, like
Databases, add `summary` (one line, shown on the topic's card). Code blocks are
small Python simulations of the mechanism being discussed, executed by build.py."""
from . import (framework, load_balancing, api_design, rate_limiting, unique_ids,
               queues, resilience, url_shortener, news_feed, chat_system)

TOPICS = [
    framework.TOPIC,
    load_balancing.TOPIC,
    api_design.TOPIC,
    rate_limiting.TOPIC,
    unique_ids.TOPIC,
    queues.TOPIC,
    resilience.TOPIC,
    url_shortener.TOPIC,
    news_feed.TOPIC,
    chat_system.TOPIC,
]
