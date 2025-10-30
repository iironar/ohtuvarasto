import unittest
from varasto import Varasto


class TestVarasto(unittest.TestCase):
    def setUp(self):
        self.varasto = Varasto(10)

    def test_konstruktori_luo_tyhjan_varaston(self):
        # https://docs.python.org/3/library/unittest.html#unittest.TestCase.assertAlmostEqual
        self.assertAlmostEqual(self.varasto.saldo, 0)

    def test_uudella_varastolla_oikea_tilavuus(self):
        self.assertAlmostEqual(self.varasto.tilavuus, 10)

    def test_lisays_lisaa_saldoa(self):
        self.varasto.lisaa_varastoon(8)

        self.assertAlmostEqual(self.varasto.saldo, 8)

    def test_lisays_lisaa_pienentaa_vapaata_tilaa(self):
        self.varasto.lisaa_varastoon(8)

        # vapaata tilaa pitäisi vielä olla tilavuus-lisättävä määrä eli 2
        self.assertAlmostEqual(self.varasto.paljonko_mahtuu(), 2)

    def test_ottaminen_palauttaa_oikean_maaran(self):
        self.varasto.lisaa_varastoon(8)

        saatu_maara = self.varasto.ota_varastosta(2)

        self.assertAlmostEqual(saatu_maara, 2)

    def test_ottaminen_lisaa_tilaa(self):
        self.varasto.lisaa_varastoon(8)

        self.varasto.ota_varastosta(2)

        # varastossa pitäisi olla tilaa 10 - 8 + 2 eli 4
        self.assertAlmostEqual(self.varasto.paljonko_mahtuu(), 4)
    
    def test_virheellinen_tilavuus_nollataan(self):
        
        self.varasto = Varasto(0.0)
        self.assertAlmostEqual(self.varasto.tilavuus, 0.0)
        
        self.varasto = Varasto(-1)
        self.assertAlmostEqual(self.varasto.tilavuus, 0.0)
    
    def test_virheellinen_saldo_nollataan(self):
        
        self.varasto = Varasto(1, -1)
        self.assertAlmostEqual(self.varasto.saldo, 0.0)
    
    def test_negatiivinen_lisays_mitatoidaan(self):
        
        self.varasto.lisaa_varastoon(2)
        self.varasto.lisaa_varastoon(-1)
        self.assertAlmostEqual(self.varasto.saldo, 2)
    
    def test_lisayksen_ylijaama_poistetaan(self):
        
        self.varasto.lisaa_varastoon(20)
        self.assertAlmostEqual(self.varasto.saldo, 10)
    
    def test_negatiivinen_otto_palauttaa_nolla(self):
        
        self.assertAlmostEqual(self.varasto.ota_varastosta(-1), 0)
        self.assertAlmostEqual(self.varasto.ota_varastosta(0), 0)
    
    def test_liiallinen_otto_palauttaa_koko_saldon(self):
        
        self.varasto.lisaa_varastoon(10)
        self.assertAlmostEqual(self.varasto.ota_varastosta(11), 10)
    
    def test_str_toimii(self):
        
        palautettava_string = "saldo = 0, vielä tilaa 10"
        self.assertEqual(palautettava_string, str(self.varasto))
        
        self.varasto.lisaa_varastoon(6)
        palautettava_string = "saldo = 6, vielä tilaa 4"
        self.assertEqual(palautettava_string, str(self.varasto)) 
                
        
            
        
            
