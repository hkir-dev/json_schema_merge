import json

from deepmerge import Merger
from abc import ABC, abstractmethod, ABCMeta


class BaseSchemaMergeStrategy(ABC):

    @abstractmethod
    def merge(self, base_schema, extension_schema, print_merged_schema=False, print_path=None):
        pass


class DeepmergeStrategy(BaseSchemaMergeStrategy):

    def unique_append(config, path, base, nxt):
        """ a list strategy to append only unique elements. """
        if len(nxt) > 0:
            if isinstance(nxt[0], str):
                base.extend(x for x in nxt if x not in base)
            else:
                base.extend(nxt)
        return base

    my_merger = Merger(
        # pass in a list of tuple, with the
        # strategies you are looking to apply
        # to each type.
        [
            (list, [unique_append, "append"]),
            (dict, ["merge"]),
            (set, ["union"])
        ],
        # next, choose the fallback strategies,
        # applied to all other types:
        ["use_existing"],
        # finally, choose the strategies in
        # the case where the types conflict:
        ["use_existing"]
    )

    def merge(self, base_schema, extension_schema, print_merged_schema=False, print_path=None):
        merged_schema = self.my_merger.merge(base_schema, extension_schema)

        if print_merged_schema:
            with open(print_path, "w") as outfile:
                json_object = json.dumps(merged_schema, indent=4)
                outfile.write(json_object)
        return merged_schema


