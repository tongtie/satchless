from satchless.item import ItemSet, ItemLine


class CartLine(ItemLine):

    def __init__(self, product, quantity, data=None):
        self.product = product
        self.quantity = quantity
        self.data = data

    def __eq__(self, other):
        if not isinstance(other, CartLine):
            return NotImplemented

        return (self.product == other.product and
                self.quantity == other.quantity and
                self.data == other.data)

    def __ne__(self, other):
        return not self == other  # pragma: no cover

    def __repr__(self):
        return 'CartLine(product=%r, quantity=%r, data=%r)' % (
            self.product, self.quantity, self.data)

    def __getstate__(self):
        return (self.product, self.quantity, self.data)

    def __setstate__(self, data):
        self.product, self.quantity, self.data = data

    def get_quantity(self):
        return self.quantity

    def get_price_per_item(self, **kwargs):
        return self.product.get_price(**kwargs)


class Cart(ItemSet):

    SESSION_KEY = 'cart'
    modified = False
    state = None

    def __init__(self, items=None):
        self.state = []
        self.modified = True
        items = items or []
        for l in items:
            self.add_line(l.product, l.quantity, l.data, replace=True)

    def __repr__(self):
        return 'Cart(%r)' % (list(self),)

    def __iter__(self):
        for cart_line in self.state:
            yield cart_line

    def __getstate__(self):
        return self.state

    def __setstate__(self, state):
        self.state = state

    def __len__(self):
        return len(self.state)

    def __nonzero__(self):
        return bool(self.state)

    def __getitem__(self, key):
        return self.state[key]

    def count(self):
        return sum([item.get_quantity() for item in self.state])

    def check_quantity(self, product, quantity, data=None):
        return True

    def create_line(self, product, quantity=0, data=None):
        return CartLine(product, quantity, data=None)

    def get_line(self, product, data=None):
        return next(
            (cart_line for cart_line in self.state
             if cart_line.product == product and cart_line.data == data ),
            None)

    def get_or_create_line(self, product, quantity, data=None):
        cart_line = self.get_line(product, data)
        if cart_line:
            return (False, cart_line)
        else:
            return (True, self.create_line(product, quantity, data))

    def add_line(self, product, quantity, data=None, replace=False):
        created, cart_line = self.get_or_create_line(product, 0, data)

        if replace:
            cart_line.quantity = quantity
        else:
            cart_line.quantity += quantity

        if cart_line.quantity < 0:
            raise ValueError('%r is not a valid quantity' % (quantity,))

        self.check_quantity(product, quantity, data)

        if not cart_line.quantity and not created:
            self.state.remove(cart_line)
            self.modified = True
        elif cart_line.quantity and created:
            self.state.append(cart_line)
            self.modified = True
        elif not created:
            self.modified = True

