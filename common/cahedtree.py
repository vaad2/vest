class CacheTreeItem(object):
    def __init__(self, pos, item, ctree):
        self.item = item
        self.ctree = ctree
        self.pos = pos
        self.open = False
        self.close = 0

    def url(self):
        if self.item.link:
            return self.item.link.url
        return self.item.url

    def children(self, **kwargs):
        include_self = kwargs.get('include_self', False)

        min_level = kwargs.get('min_level', 0)
        max_level = kwargs.get('max_level', 100)

        lev = self.item.level
        pos = self.pos + 1
        children = []

        if include_self:
            children.append(self)

        tl = self.ctree.tree_list

        while pos < len(tl):
            cti = tl[pos]
            pos += 1

            if cti.item.level < min_level or cti.item.level > max_level:
                continue

            if cti.item.level <= lev:
                break

            children.append(cti)

        return children


class CacheTree(object):
    def __init__(self, tree, url=None):
        self.tree_map = {}
        self.tree_list = []

        self.tree = tree

        prev_item = None

        active_item = None

        for i, item in enumerate(tree):
            cti = CacheTreeItem(i, item, self)

            self.tree_map[item.pk] = cti
            self.tree_list.append(cti)

            if prev_item and prev_item.item.level < item.level:
                prev_item.open = True

            if prev_item and prev_item.item.level > item.level:
                prev_item.close = prev_item.item.level - item.level

            prev_item = cti

            if url == cti.url():
                active_item = item
                cti.active = True
                cti.current = True

        if active_item:
            for item_pk in active_item.path.split(','):
                if item_pk in self.tree_map:
                    self.tree_map[item_pk].active = True

        cti.close = item.level - tree[0].level


    def __getitem__(self, pk):
        pk = int(pk)
        return self.tree_map.get(pk, None)

    def items__in(self, ids):
        if isinstance(ids, basestring):
            ids = ids.split(',')

        result = []
        for id in ids:
            cti = self.tree_map[int(id)]
            if cti:
                result.append(cti.item)

        return result
