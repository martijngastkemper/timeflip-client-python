from facet_action import FacetAction, Actions
from functools import cached_property
import productive


class TimeEntryPicker:

    def __init__(self, time_entries: list[productive.TimeEntry]):
        self.time_entries = time_entries

    @cached_property
    def get_facet_actions(self) -> list[FacetAction]:
        actions = [FacetAction(Actions.STOP, productive.TimeEntry(123, "Pause current time entry"))]

        for k, time_entry in enumerate(self.time_entries):
            actions.append(FacetAction(Actions.START, time_entry))

        return actions

    def get_facet_action(self, identifier: int) -> FacetAction:
        return self.get_facet_actions[identifier]

    def create_option_list(self) -> str:
        output = "Pick a task to assign to this icon:\n"
        for k, facet_action in enumerate(self.get_facet_actions):
            output = output + "{0}) {1}\n".format(k, facet_action.time_entry.description)
        return output.rstrip("\n")