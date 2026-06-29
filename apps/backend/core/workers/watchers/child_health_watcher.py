from core.workers.watchers.base_watcher import BaseWatcher
from core.domain.enums import WatcherDomain


class ChildHealthWatcher(BaseWatcher):
    domain = WatcherDomain.CHILD_HEALTH

    async def _process(self, member_id, family_id, events):
        pass
