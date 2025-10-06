#!/usr/bin/env python3
"""
Google Maps SEO Geographic Boundaries Analyzer
Identifies territorial dominance radius and expansion opportunities
"""

import logging
import random
import time
import requests
import psycopg2
from dotenv import load_dotenv
import os
import math
from datetime import datetime

load_dotenv('.env')

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BotFronterasGeoSEO:
    def __init__(self):
        self.api_key = os.getenv('GOOGLE_MAPS_API_KEY')
        if not self.api_key:
            raise ValueError("GOOGLE_MAPS_API_KEY not found in .env file")
        
        # Target business configuration
        self.target_domain = os.getenv('TARGET_DOMAIN', 'yourbusiness.com')
        self.target_business_name = os.getenv('BUSINESS_NAME', 'Your Business Name')
        
        # Base location (customize in .env)
        self.base_location = {
            'name': os.getenv('BASE_CITY', 'Los Angeles, CA'),
            'lat': float(os.getenv('BASE_LAT', '33.9616')),
            'lng': float(os.getenv('BASE_LNG', '-118.3531'))
        }
        
        # Test cities organized by distance tiers
        self.ciudades_test = {
            'tier_1_immediate': [  # 0-5km - Expected dominance
                {'name': 'Inglewood', 'lat': 33.9616, 'lng': -118.3531, 'zip': '90301'},
                {'name': 'Lennox', 'lat': 33.9386, 'lng': -118.3531, 'zip': '90304'},
                {'name': 'Westchester', 'lat': 33.9589, 'lng': -118.4031, 'zip': '90045'},
                {'name': 'Ladera Heights', 'lat': 33.9989, 'lng': -118.3703, 'zip': '90056'}
            ],
            'tier_2_nearby': [  # 5-10km - Immediate expansion
                {'name': 'Hawthorne', 'lat': 33.9164, 'lng': -118.3526, 'zip': '90250'},
                {'name': 'El Segundo', 'lat': 33.9192, 'lng': -118.4165, 'zip': '90245'},
                {'name': 'Manhattan Beach', 'lat': 33.8847, 'lng': -118.4109, 'zip': '90266'},
                {'name': 'Culver City', 'lat': 34.0211, 'lng': -118.3965, 'zip': '90230'},
                {'name': 'Gardena', 'lat': 33.8883, 'lng': -118.3090, 'zip': '90247'},
                {'name': 'Lawndale', 'lat': 33.8872, 'lng': -118.3526, 'zip': '90260'}
            ],
            'tier_3_medium': [  # 10-15km - Strategic opportunity
                {'name': 'Torrance', 'lat': 33.8358, 'lng': -118.3406, 'zip': '90501'},
                {'name': 'Redondo Beach', 'lat': 33.8492, 'lng': -118.3884, 'zip': '90277'},
                {'name': 'Hermosa Beach', 'lat': 33.8622, 'lng': -118.3995, 'zip': '90254'},
                {'name': 'Marina del Rey', 'lat': 33.9803, 'lng': -118.4517, 'zip': '90292'},
                {'name': 'Playa Vista', 'lat': 33.9733, 'lng': -118.4233, 'zip': '90094'},
                {'name': 'Compton', 'lat': 33.8959, 'lng': -118.2201, 'zip': '90220'},
                {'name': 'Carson', 'lat': 33.8316, 'lng': -118.2820, 'zip': '90745'}
            ],
            'tier_4_distant': [  # 15-25km - ROI evaluation
                {'name': 'Long Beach', 'lat': 33.7701, 'lng': -118.1937, 'zip': '90802'},
                {'name': 'Venice', 'lat': 33.9850, 'lng': -118.4695, 'zip': '90291'},
                {'name': 'Santa Monica', 'lat': 34.0195, 'lng': -118.4912, 'zip': '90401'},
                {'name': 'Downey', 'lat': 33.9401, 'lng': -118.1332, 'zip': '90241'},
                {'name': 'Paramount', 'lat': 33.8894, 'lng': -118.1598, 'zip': '90723'},
                {'name': 'Lynwood', 'lat': 33.9303, 'lng': -118.2115, 'zip': '90262'}
            ]
        }
        
        # Core keywords to test dominance
        self.core_keywords = [
            'house cleaning',
            'cleaning services',
            'maid service'
        ]
        
        self.db_conn = None
        self._conectar_db()
    
    def _conectar_db(self):
        """Connect to PostgreSQL and create geographic analysis table"""
        try:
            self.db_conn = psycopg2.connect(
                host=os.getenv('DB_HOST', 'localhost'),
                database=os.getenv('DB_NAME', 'seo_analysis'),
                user=os.getenv('DB_USER', 'postgres'),
                password=os.getenv('DB_PASSWORD')
            )
            
            with self.db_conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS maps_analisis_geografico (
                        id SERIAL PRIMARY KEY,
                        fecha_analisis DATE DEFAULT CURRENT_DATE,
                        ciudad VARCHAR(100),
                        estado VARCHAR(50),
                        zip_code VARCHAR(10),
                        tier VARCHAR(50),
                        keyword VARCHAR(255),
                        aparece BOOLEAN DEFAULT FALSE,
                        posicion INTEGER,
                        distancia_km DECIMAL(6,2),
                        lat DECIMAL(10,8),
                        lng DECIMAL(11,8),
                        total_competidores INTEGER,
                        rating_promedio_competidores DECIMAL(3,2),
                        reviews_promedio_competidores INTEGER,
                        creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                self.db_conn.commit()
            logger.info("✓ Database connected - maps_analisis_geografico table created")
        except Exception as e:
            logger.error(f"Database error: {e}")
            raise
    
    def _calcular_distancia(self, lat1, lng1, lat2, lng2):
        """Calculate distance in km using Haversine formula"""
        if not all([lat1, lng1, lat2, lng2]):
            return 0
        
        dlat = math.radians(lat2 - lat1)
        dlng = math.radians(lng2 - lng1)
        
        a = (math.sin(dlat/2) * math.sin(dlat/2) +
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
             math.sin(dlng/2) * math.sin(dlng/2))
        
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        distance = 6371 * c  # Earth radius in km
        
        return distance
    
    def _es_tu_negocio(self, place):
        """Check if place matches your business"""
        nombre = place.get('name', '').lower()
        business_terms = os.getenv('BUSINESS_KEYWORDS', 'your business').lower().split(',')
        
        return any(term.strip() in nombre for term in business_terms)
    
    def analizar_ciudad(self, ciudad, keyword, tier):
        """Analyze Maps presence for a specific city"""
        logger.info(f"  Analyzing: {ciudad['name']} - '{keyword}'")
        
        try:
            url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
            
            params = {
                'location': f"{ciudad['lat']},{ciudad['lng']}",
                'radius': 8000,  # 8km radius
                'keyword': keyword,
                'type': 'establishment',
                'key': self.api_key
            }
            
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                
                if data['status'] == 'OK':
                    places = data.get('results', [])
                    
                    # Calculate distance from base
                    distancia = self._calcular_distancia(
                        self.base_location['lat'],
                        self.base_location['lng'],
                        ciudad['lat'],
                        ciudad['lng']
                    )
                    
                    # Find your business
                    tu_posicion = None
                    for idx, place in enumerate(places[:20]):
                        if self._es_tu_negocio(place):
                            tu_posicion = idx + 1
                            break
                    
                    # Competitor statistics
                    competidores = [p for p in places if not self._es_tu_negocio(p)]
                    rating_promedio = sum(p.get('rating', 0) for p in competidores) / len(competidores) if competidores else 0
                    reviews_promedio = sum(p.get('user_ratings_total', 0) for p in competidores) / len(competidores) if competidores else 0
                    
                    resultado = {
                        'ciudad': ciudad['name'],
                        'zip': ciudad.get('zip', ''),
                        'tier': tier,
                        'keyword': keyword,
                        'aparece': tu_posicion is not None,
                        'posicion': tu_posicion,
                        'distancia_km': round(distancia, 2),
                        'lat': ciudad['lat'],
                        'lng': ciudad['lng'],
                        'total_competidores': len(places),
                        'rating_promedio': round(rating_promedio, 2),
                        'reviews_promedio': int(reviews_promedio)
                    }
                    
                    # Log result
                    if tu_posicion:
                        logger.info(f"    ✅ Position #{tu_posicion} ({distancia:.1f}km)")
                    else:
                        logger.info(f"    ❌ Not found ({distancia:.1f}km)")
                    
                    # Save to database
                    self._guardar_resultado(resultado)
                    
                    return resultado
            
            return None
            
        except Exception as e:
            logger.error(f"    Error: {e}")
            return None
    
    def _guardar_resultado(self, resultado):
        """Save result to database"""
        try:
            with self.db_conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO maps_analisis_geografico
                    (ciudad, zip_code, tier, keyword, aparece, posicion, distancia_km,
                     lat, lng, total_competidores, rating_promedio_competidores,
                     reviews_promedio_competidores)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    resultado['ciudad'],
                    resultado['zip'],
                    resultado['tier'],
                    resultado['keyword'],
                    resultado['aparece'],
                    resultado['posicion'],
                    resultado['distancia_km'],
                    resultado['lat'],
                    resultado['lng'],
                    resultado['total_competidores'],
                    resultado['rating_promedio'],
                    resultado['reviews_promedio']
                ))
                self.db_conn.commit()
        except Exception as e:
            logger.error(f"Save error: {e}")
            self.db_conn.rollback()
    
    def ejecutar_analisis_fronteras(self):
        """Execute complete geographic boundaries analysis"""
        logger.info("=" * 80)
        logger.info("🗺️ GEOGRAPHIC BOUNDARIES ANALYSIS - GOOGLE MAPS")
        logger.info(f"📍 Base: {self.base_location['name']}")
        logger.info(f"🎯 Business: {self.target_business_name}")
        logger.info(f"🔍 Keywords: {', '.join(self.core_keywords)}")
        logger.info("=" * 80)
        
        resultados_totales = []
        
        for tier_name, ciudades in self.ciudades_test.items():
            logger.info(f"\n{'='*60}")
            logger.info(f"📊 {tier_name.replace('_', ' ').upper()}")
            logger.info(f"{'='*60}")
            
            for ciudad in ciudades:
                for keyword in self.core_keywords:
                    resultado = self.analizar_ciudad(ciudad, keyword, tier_name)
                    if resultado:
                        resultados_totales.append(resultado)
                    
                    # Pause to avoid rate limits
                    time.sleep(random.uniform(1.5, 3))
        
        # Generate reports
        self._generar_mapa_dominio(resultados_totales)
        self._generar_recomendaciones_expansion(resultados_totales)
        
        return resultados_totales
    
    def _generar_mapa_dominio(self, resultados):
        """Generate visual dominance map"""
        logger.info("\n" + "=" * 80)
        logger.info("🗺️ TERRITORIAL DOMINANCE MAP")
        logger.info("=" * 80)
        
        apariciones = [r for r in resultados if r['aparece']]
        
        if apariciones:
            distancia_max = max(r['distancia_km'] for r in apariciones)
            distancia_min = min(r['distancia_km'] for r in apariciones)
            posicion_promedio = sum(r['posicion'] for r in apariciones) / len(apariciones)
            
            logger.info(f"\n📏 DOMINANCE RADIUS:")
            logger.info(f"   Min distance where you appear: {distancia_min:.1f}km")
            logger.info(f"   Max distance where you appear: {distancia_max:.1f}km")
            logger.info(f"   Effective dominance radius: ~{distancia_max:.0f}km")
            logger.info(f"   Average Maps position: #{posicion_promedio:.1f}")
            
            logger.info(f"\n🎯 DOMINANCE BY ZONE:")
            
            for tier in ['tier_1_immediate', 'tier_2_nearby', 'tier_3_medium', 'tier_4_distant']:
                tier_apariciones = [r for r in apariciones if r['tier'] == tier]
                tier_total = len([r for r in resultados if r['tier'] == tier])
                
                if tier_total > 0:
                    cobertura = (len(tier_apariciones) / tier_total) * 100
                    tier_label = tier.replace('_', ' ').upper()
                    
                    logger.info(f"\n   {tier_label}:")
                    logger.info(f"   Coverage: {len(tier_apariciones)}/{tier_total} searches ({cobertura:.0f}%)")
                    
                    if tier_apariciones:
                        ciudades = set(r['ciudad'] for r in tier_apariciones)
                        for ciudad in sorted(ciudades):
                            ciudad_results = [r for r in tier_apariciones if r['ciudad'] == ciudad]
                            posiciones = [r['posicion'] for r in ciudad_results]
                            pos_promedio = sum(posiciones) / len(posiciones)
                            logger.info(f"      ✅ {ciudad}: Pos #{pos_promedio:.1f}")
        else:
            logger.info("\n❌ No appearances found in any analyzed city")
    
    def _generar_recomendaciones_expansion(self, resultados):
        """Generate strategic expansion recommendations"""
        logger.info("\n" + "=" * 80)
        logger.info("🎯 TERRITORIAL EXPANSION STRATEGY")
        logger.info("=" * 80)
        
        no_apariciones = [r for r in resultados if not r['aparece']]
        ciudades_oportunidad = {}
        
        for ciudad in set(r['ciudad'] for r in no_apariciones):
            ciudad_data = [r for r in no_apariciones if r['ciudad'] == ciudad][0]
            ciudades_oportunidad[ciudad] = {
                'distancia': ciudad_data['distancia_km'],
                'tier': ciudad_data['tier'],
                'competidores': ciudad_data['total_competidores'],
                'rating_competidores': ciudad_data['rating_promedio'],
                'reviews_competidores': ciudad_data['reviews_promedio']
            }
        
        ciudades_ordenadas = sorted(ciudades_oportunidad.items(), key=lambda x: x[1]['distancia'])
        
        logger.info(f"\n🎯 TOP 10 EXPANSION OPPORTUNITIES:")
        logger.info("   (Nearby cities where you DON'T appear)\n")
        
        for i, (ciudad, data) in enumerate(ciudades_ordenadas[:10], 1):
            dificultad = "EASY" if data['reviews_competidores'] < 100 else "MEDIUM" if data['reviews_competidores'] < 200 else "HARD"
            
            logger.info(f"   {i}. {ciudad} ({data['distancia']:.1f}km)")
            logger.info(f"      Tier: {data['tier'].replace('_', ' ')}")
            logger.info(f"      Competitors: {data['competidores']}")
            logger.info(f"      Avg rating: {data['rating_competidores']:.1f}⭐")
            logger.info(f"      Avg reviews: {data['reviews_competidores']}")
            logger.info(f"      Difficulty: {dificultad}\n")
        
        logger.info("\n" + "=" * 80)
        logger.info("✅ BOUNDARIES ANALYSIS COMPLETED")
        logger.info("=" * 80)
    
    def cerrar(self):
        if self.db_conn:
            self.db_conn.close()

def main():
    bot = None
    try:
        bot = BotFronterasGeoSEO()
        bot.ejecutar_analisis_fronteras()
    except KeyboardInterrupt:
        logger.info("\n⏹️ Interrupted by user")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if bot:
            bot.cerrar()

if __name__ == "__main__":
    main()
