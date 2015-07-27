from ..testcase import BaseTestCase


class ManyToManyTestCase(BaseTestCase):
    def setUp(self):
        super(ManyToManyTestCase, self).setUp()

        from django.db import models as dj_models
        from djangostdnet import models

        class DjangoModelA(dj_models.Model):
            name = dj_models.CharField(max_length=255)

            class Meta:
                app_label = self.app_label

        class DjangoModelB(dj_models.Model):
            neighbors = dj_models.ManyToManyField(DjangoModelA)

            class Meta:
                app_label = self.app_label

        class ModelA(models.Model):
            class Meta:
                django_model = DjangoModelA

        class ModelB(models.Model):
            class Meta:
                django_model = DjangoModelB

        self.finish_defining_models()
        self.create_table_for_model(DjangoModelA)
        self.create_table_for_model(DjangoModelB)
        for field in DjangoModelB._meta.many_to_many:
            self.create_table_for_model(field.rel.through)

        self.dj_model_a = DjangoModelA
        self.dj_model_b = DjangoModelB
        self.std_model_a = ModelA
        self.std_model_b = ModelB

    def test_many_to_many_from_django(self):
        dj_obj = self.dj_model_a.objects.create(name='foo')
        neighbor = self.dj_model_b.objects.create()
        neighbor.neighbors.add(dj_obj)

        computed_neighbor = dj_obj.djangomodelb_set.get()
        self.assertEquals(neighbor, computed_neighbor, "Cyclic Check of Relation on Django")
        self.assertEquals(computed_neighbor.neighbors.get(), dj_obj, "Cyclic Check of Relation on Django")

        obj = self.std_model_a.objects.get()
        neighbor_std = self.std_model_b.objects.get()

        computed_neighbor_std = obj.modelb_set.get()
        self.assertEquals(neighbor_std, computed_neighbor_std, "Cyclic Check of Relation on Stdnet")
        self.assertEquals(computed_neighbor_std.neighbors.get(), obj, "Cyclic Check of Relation on Stdnet")

        neighbor.neighbors.remove(dj_obj)
        self.assertEquals(len(obj.modelb_set.all()), 0)
        self.assertEquals(len(neighbor_std.neighbors.all()), 0)

    def test_many_to_many_from_stdnet(self):
        std_obj = self.std_model_a.objects.new(name='foo')
        neighbor = self.std_model_b.objects.new()
        neighbor.neighbors.add(std_obj)

        computed_neighbor = std_obj.modelb_set.get()
        self.assertEquals(neighbor, computed_neighbor, "Cyclic Check of Relation on Stdnet")
        self.assertEquals(computed_neighbor.neighbors.get(), std_obj, "Cyclic Check of Relation on Stdnet")

        dj_obj = self.dj_model_a.objects.get()
        dj_neighbor = self.dj_model_b.objects.get()

        dj_computed_neighbor = dj_obj.djangomodelb_set.get()
        self.assertEquals(dj_neighbor, dj_computed_neighbor, "Cyclic Check of Relation on Django")
        self.assertEquals(dj_computed_neighbor.neighbors.get(), dj_obj, "Cyclic Check of Relation on Django")

        neighbor.neighbors.remove(std_obj)
        self.assertEquals(len(dj_obj.djangomodelb_set.all()), 0)
        self.assertEquals(len(dj_neighbor.neighbors.all()), 0)


# XXX create a test with specified many-to-many back ref
