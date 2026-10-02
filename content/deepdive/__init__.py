"""Python Deep Dive: one module per topic, in the order they appear on the site.
See _blocks.py for the schema."""
from . import (gil, memory, bytecode, object_model, dunder_methods, descriptors, metaclasses,
               mro, slots_dataclasses_typing, decorators, generators, context_managers,
               imports, async_internals, asyncio_pitfalls)

TOPICS = [
    gil.TOPIC,
    memory.TOPIC,
    bytecode.TOPIC,
    object_model.TOPIC,
    dunder_methods.TOPIC,
    descriptors.TOPIC,
    metaclasses.TOPIC,
    mro.TOPIC,
    slots_dataclasses_typing.TOPIC,
    decorators.TOPIC,
    generators.TOPIC,
    context_managers.TOPIC,
    imports.TOPIC,
    async_internals.TOPIC,
    asyncio_pitfalls.TOPIC,
]
