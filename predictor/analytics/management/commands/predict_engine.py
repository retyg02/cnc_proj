import time, datetime
from django.core.management.base import BaseCommand
from django.db import connection 
from django.conf import settings
from pymongo import MongoClient 

class Command(BaseCommand):
    help = 'ИИ-Предиктор: Анализ логов телеметрии и предсказание аварий ЧПУ'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🚀 ИИ-Движок Django успешно запущен...'))
        
        try:
            mongo_client = MongoClient(settings.MONGO_HOST, settings.MONGO_PORT)
            mongo_db = mongo_client[settings.MONGO_DB_NAME]
            mongo_logs = mongo_db['aggregated_logs']
            mongo_logs.create_index("created_at", expireAfterSeconds=3600)
            self.stdout.write(self.style.SUCCESS('📥 Успешное подключение к MongoDB!'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Ошибка подключения к MongoDB: {e}'))
            return

        while True:
            try:
                self.stdout.write(self.style.WARNING('\n🔄 Сканирование таблицы machine_logs в PostgreSQL...'))
                
                with connection.cursor() as cursor:
                    cursor.execute("SELECT id, machine_id, action_text FROM machine_logs ORDER BY id DESC LIMIT 50")
                    rows = cursor.fetchall()
                    cursor.execute("""
                        DELETE FROM machine_logs 
                        WHERE created_at < NOW() - INTERVAL '10 minutes';
                    """)
                
                if rows:
                    self.stdout.write(f"Найдено {len(rows)} записей в Postgres. Переносим в MongoDB...")                    
                    
                    for row in rows:
                        log_id, machine_id, action_text = row                        
                        
                        log_document = {
                            "postgres_id": log_id,
                            "machine_id": machine_id,
                            "log_text": action_text,
                            "analyzed": False,
                            "created_at": datetime.datetime.utcnow()
                        }
                        
                        if not mongo_logs.find_one({"postgres_id": log_id}):
                            mongo_logs.insert_one(log_document)
                
                
                # =======================================================
                self.stdout.write(self.style.SUCCESS('\n📊 Запуск частотного ИИ-анализа логов из MongoDB...'))
                
                uncommented_logs = list(mongo_logs.find({"analyzed": False}))
                
                if uncommented_logs:
                    machine_fault_scores = {}
                    
                    danger_keywords = ['сбой', 'ошибка', 'таймаут', 'задержка', 'не отвечает', 'Превышен температурный порог']
                    
                    for doc in uncommented_logs:
                        m_id = doc['machine_id']
                        text = doc['log_text'].lower() 
                        
                        if m_id not in machine_fault_scores:
                            machine_fault_scores[m_id] = 0
                            
                        for word in danger_keywords:
                            if word in text:
                                machine_fault_scores[m_id] += 1
                                break 
                        
                        mongo_logs.update_one({"_id": doc["_id"]}, {"$set": {"analyzed": True}})
                    
                    for m_id, score in machine_fault_scores.items():
                        if score == 0:
                            probability = 5 
                            status_text = "СТАБИЛЬНЫЙ (Зеленый уровень)"
                            style_func = self.style.SUCCESS
                        elif score <= 2:
                            probability = 35 
                            status_text = "ВНИМАНИЕ: Наблюдаются микросбои сети (Желтый уровень)"
                            style_func = self.style.WARNING
                        else:
                            probability = min(score * 20, 95) 
                            status_text = "🚨 КРИТИЧЕСКИЙ РИСК: Прогрессирующий отказ контроллера! (Красный уровень)"
                            style_func = self.style.ERROR
                        
                        self.stdout.write(style_func(
                            f"[ИИ ВЕРДИКТ] Станок ЧПУ #{m_id} -> Статус: {status_text} | "
                            f"Вероятность аварийного останова: {probability}%"
                        ))
                else:
                    self.stdout.write(self.style.HTTP_INFO('ℹ️ Нет новых необработанных логов в MongoDB.'))

            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Критическая ошибка в цикле ИИ: {e}'))
            
            time.sleep(10)
