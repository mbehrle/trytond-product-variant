# -*- coding: utf-8 -*-
# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.pool import PoolMeta, Pool
from trytond.model import fields
from trytond.pyson import Eval

__all__ = ['Template', 'Product']

STATES = {
    'readonly': ~Eval('active', True),
}
DEPENDS = ['active']


class Template:
    __metaclass__ = PoolMeta
    __name__ = "product.template"

    @classmethod
    def __setup__(cls):
        super(Template, cls).__setup__()
        cls.list_price = fields.Function(
            fields.Numeric("List Price"), 'get_prices'
        )
        cls.cost_price = fields.Function(
            fields.Numeric("Cost Price"), 'get_prices'
        )

    def get_prices(self, name):
        '''Reached here! Just raise an exception to know what logic is using
        product template's prices?
        '''
        raise Exception(
            "Product prices must be taken from product.product aka Variant"
        )


class Product:
    __metaclass__ = PoolMeta
    __name__ = "product.product"

    list_price = fields.Property(
        fields.Numeric(
            'List Price', digits=(16, 4), required=True,
            states=STATES, depends=DEPENDS
        )
    )
    cost_price = fields.Property(
        fields.Numeric(
            'Cost Price', digits=(16, 4), required=True,
            states=STATES, depends=DEPENDS
        )
    )

    name = fields.Function(
        fields.Char('Name'),
        getter='on_change_with_name', searcher='search_rec_name'
    )

    variant_name = fields.Char(
        'Variant Name', translate=True,
        select=True, states={
            'readonly': ~Eval('active', True),
        }, depends=['active']
    )

    @fields.depends('variant_name', 'template')
    def on_change_with_name(self, name=None):  # pragma: no cover
        '''
        This method returns the variant_name` if it is set,
        else it returns the template name.
        '''
        return self.variant_name or self.template.name

    @classmethod
    def search_rec_name(cls, name, clause):
        '''
        Downstream implementation of `search_rec_name` which adds the
        variant_name field to the domain.
        '''
        domain = super(Product, cls).search_rec_name(name, clause)
        domain.append(('variant_name', ) + tuple(clause[1:]))
        return domain

    @classmethod
    def set_template(cls, products, name, value):
        '''
        Provide a generic setter for function fields when using
        template fields on products. (In analogy to get_template,
        search_template for the use in downstream modules)
        '''
        Template = Pool().get('product.template')
        Template.write([p.template for p in products], {
                name: value,
                })
