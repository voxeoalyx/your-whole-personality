"""Scientific correctness checks on comparisons, geometry and baseline fitting."""
import math
import unittest
from analyze_experiment2 import ranks, rho, dissim, hellinger, linear_fit, venue_category
from experiment2 import polygon, inside, distance, centroid


class ResearchChecks(unittest.TestCase):
    def test_ties_and_constant_are_not_invented_signal(self):
        self.assertEqual(ranks([3,1,1]),[3,1.5,1.5])
        self.assertIsNone(rho([1,1,1],[1,2,3]))

    def test_monotone_normalization_keeps_rank_comparison(self):
        self.assertAlmostEqual(rho([1,2,3,4],[1,4,9,16]),1)
        self.assertAlmostEqual(dissim({'a':1,'b':2},{'a':2,'b':1}),1)

    def test_missing_candidate_is_never_zero(self):
        self.assertIsNone(dissim({'a':1,'b':0},{'a':1}))
        self.assertEqual(dissim({'a':1,'b':0},{'a':1,'b':0}),0)

    def test_inventory_proportions_and_missing(self):
        self.assertEqual(hellinger({'cafe':1},{'cafe':10}),0)
        self.assertAlmostEqual(hellinger({'cafe':1},{'shop':1}),1)
        self.assertIsNone(hellinger({}, {'cafe':2}))
        self.assertIsNone(venue_category({'amenity':'parking'}))
        self.assertIsNone(venue_category({'leisure':'swimming_pool','access':'private'}))
        self.assertEqual(venue_category({'amenity':'restaurant'}),'restaurant')

    def test_geodesic_circle_and_point_containment(self):
        g=polygon(28.5,-81.3)
        self.assertTrue(inside(-81.3,28.5,g))
        self.assertFalse(inside(-81.2,28.5,g))
        for lon,lat in g['coordinates'][0]:
            self.assertAlmostEqual(distance({'lat':28.5,'lon':-81.3},{'lat':lat,'lon':lon}),1000,delta=.002)
        lon,lat=centroid(g['coordinates'][0]);self.assertAlmostEqual(lon,-81.3,places=5)
        shifted=polygon(28.5,-81.3,east=200);slon,slat=centroid(shifted['coordinates'][0])
        self.assertAlmostEqual(distance({'lat':lat,'lon':lon},{'lat':slat,'lon':slon}),200,delta=.02)

    def test_ols_training_scale_and_extrapolation(self):
        fn=linear_fit([[i,1] for i in range(10)],[2+3*i for i in range(10)])
        self.assertAlmostEqual(fn([12,1]),38,places=6)


if __name__=='__main__': unittest.main()
