from core.workers.watchers.base_watcher import BaseWatcher
from core.domain.enums import WatcherDomain

class FamilyCareWatcher(BaseWatcher):
    domain = WatcherDomain.FAMILY_CARE
    async def _process(self, member_id, family_id, events): pass
