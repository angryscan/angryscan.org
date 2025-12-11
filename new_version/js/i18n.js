/**
 * Internationalization (i18n) translations
 * Russian and English have custom translations
 * Other languages use Google Translate from English
 */

const I18N = {
    en: {
        // Site metadata
        site: {
            title: 'Angry Data Scanner - Sensitive Data Scanner for Mac, Windows and Linux',
            description: 'Advanced sensitive data discovery tool combining personal data discovery, payment card discovery, and passwords finder in one solution. Comprehensive data detector for compliance and security.'
        },
        // Navigation
        nav: {
            dataDiscovery: 'Data Discovery',
            features: 'Features',
            download: 'Download',
            github: 'GitHub',
            contactUs: 'Contact us'
        },
        // Hero section
        hero: {
            badge: 'Free Open Source',
            title: 'Sensitive Data Discovery Tool',
            description: 'Angry Data Scanner is a free sensitive data discovery tool designed to automatically find PII (Personally Identifiable Information), PHI (Protected Health Information) and intellectual property using advanced pattern matching. Perform unified data searches across local folders, web pages, AWS S3 buckets, and databases.',
            features: {
                simple: 'Intuitive design meant for speed and ease of use.',
                twoClicks: 'Detect sensitive data instantly with just 2 clicks.',
                noAdmin: 'No admin rights or installation required.',
                crossPlatform: 'Works seamlessly on Linux macOS and Windows.',
                privacy: 'All scanning happens locally. Your data never leaves your PC'
            },
            cta: {
                download: 'Download Now',
                github: 'View on GitHub'
            }
        },
        // Sections
        sections: {
            discovery: {
                title: 'Sensitive data discovery',
                description: 'Angry Data Scanner can detect various types of sensitive data across multiple categories',
                filterByCountry: 'Filter by country',
                all: 'All',
                international: 'International',
                russia: 'Russia',
                unitedStates: 'United States',
                china: 'China'
            },
            fileTypes: {
                title: 'Supported file types'
            },
            dataSources: {
                title: 'Supported data sources',
                sources: [
                    { connector: 'Network Folder', description: 'Scans files on remote directory like Windows environment' },
                    { connector: 'HDD/SDD', description: 'Scan local hard drive' },
                    { connector: 'S3', description: 'Scan files in S3' },
                    { connector: 'HTTP/HTTPS', description: 'Scans web site content' }
                ]
            },
            features: {
                title: 'Key features'
            },
            useCases: {
                title: 'Real life use cases',
                cases: [
                    'A leak hunting team scans network folder and ensure that it does not contain source code',
                    'An employee finds and deletes files containing card numbers to comply with PCI DSS',
                    'A banking employee scans network folder to ensure that it does not contain PII of VIP clients',
                    'A boss scans a shared folder of the sales team so they don\'t have client contacts there',
                    'Law enforcements need to discover a traces of cryptocurrency on a laptop',
                    'A cybersecurity officer need to validate that the database does not contain a personal data'
                ]
            },
            download: {
                title: 'Download',
                systemRequirements: 'System Requirements: Windows, Linux, MacOS | 400MB HDD | 4GB RAM | 1.3Ghz CPU'
            }
        },
        // Categories
        categories: {
            personalDataNumbers: 'Personal Data (numbers)',
            personalDataText: 'Personal Data (text)',
            pciDss: 'PCI DSS',
            bankingSecrecy: 'Banking Secrecy',
            itAssets: 'IT Assets',
            customSignatures: 'Custom Signatures',
            customSignaturesDesc: 'It is possible to add custom data search signatures using plain text:',
            customSignaturesOr: 'or any other.',
            customSignaturesExamples: ['Secret', 'Password', 'Central bank']
        },
        // Table headers
        tableHeaders: {
            dataType: 'Data type',
            localName: 'Local name',
            country: 'Country',
            example: 'Example',
            fileType: 'File Type',
            fileFormat: 'File Format',
            connector: 'Connector',
            description: 'Description'
        },
        // Features
        features: {
            ranking: {
                title: 'Ranking',
                description: 'Scanner shows high-value files first'
            },
            history: {
                title: 'View scanning history',
                description: 'Track all your previous scans'
            },
            export: {
                title: 'Export results',
                description: 'Download results in a CSV file'
            },
            schedule: {
                title: 'Schedule scans',
                description: 'Automate your scanning process'
            },
            matchers: {
                title: 'Configurable matchers',
                description: 'Configure PII, PCI DSS and other matchers'
            },
            formats: {
                title: 'Multiple file formats',
                description: 'Configure file formats (pdf, excel, etc.)'
            }
        },
        // Footer
        footer: {
            copyright: '© 2025, by admin@angryscan.org'
        },
        // Empty message
        emptyMessage: 'No data available for selected country'
    },
    ru: {
        // Site metadata
        site: {
            title: 'Angry Data Scanner - Программа поиска конфиденциальных данных для Mac, Windows и Linux',
            description: 'Инструмент поиска данных. С его помощью можно найти персональные данные, данные банковских карт и другие конфиденциальные данные в папках, S3, базах данных, веб-страницах.'
        },
        // Navigation
        nav: {
            dataDiscovery: 'Обнаружение данных',
            features: 'Возможности',
            download: 'Скачать',
            github: 'GitHub',
            contactUs: 'Связаться с нами'
        },
        // Hero section
        hero: {
            badge: 'Free Open Source',
            title: 'Бесплатная программа для быстрого поиска конфиденциальных данных',
            description: 'Бесплатный инструмент для автоматического поиска PII, PHI и интеллектуальной собственности с помощью расширенного сопоставления шаблонов. Выполняйте поиск данных в локальных папках, веб-страницах, AWS S3 и базах данных.',
            features: {
                simple: 'Интуитивный дизайн для скорости и удобства.',
                twoClicks: 'Обнаружение конфиденциальных данных за 2 клика.',
                noAdmin: 'Не требуются права администратора или установка.',
                crossPlatform: 'Работает на Linux, macOS и Windows.',
                privacy: 'Все сканирование происходит локально. Данные не покидают ваш компьютер'
            },
            cta: {
                download: 'Скачать сейчас',
                github: 'Посмотреть на GitHub'
            }
        },
        // Sections
        sections: {
            discovery: {
                title: 'Обнаружение конфиденциальных данных',
                description: 'Angry Data Scanner может обнаруживать различные типы конфиденциальных данных в нескольких категориях',
                filterByCountry: 'Фильтр по стране',
                all: 'Все',
                international: 'Международные',
                russia: 'Россия',
                unitedStates: 'Соединенные Штаты',
                china: 'Китай'
            },
            fileTypes: {
                title: 'Поддерживаемые типы файлов'
            },
            dataSources: {
                title: 'Поддерживаемые источники данных',
                sources: [
                    { connector: 'Сетевая папка', description: 'Сканирует файлы в удаленной директории, например в среде Windows' },
                    { connector: 'HDD/SSD', description: 'Сканирование локального жесткого диска' },
                    { connector: 'S3', description: 'Сканирование файлов в S3' },
                    { connector: 'HTTP/HTTPS', description: 'Сканирование содержимого веб-сайта' }
                ]
            },
            features: {
                title: 'Ключевые возможности'
            },
            useCases: {
                title: 'Реальные случаи использования',
                cases: [
                    'Команда по поиску утечек сканирует сетевую папку и убеждается, что она не содержит исходный код',
                    'Сотрудник находит и удаляет файлы, содержащие номера карт, для соответствия PCI DSS',
                    'Банковский сотрудник сканирует сетевую папку, чтобы убедиться, что она не содержит PII VIP-клиентов',
                    'Руководитель сканирует общую папку отдела продаж, чтобы там не было контактов клиентов',
                    'Правоохранительным органам нужно обнаружить следы криптовалюты на ноутбуке',
                    'Специалист по кибербезопасности должен проверить, что база данных не содержит персональных данных'
                ]
            },
            download: {
                title: 'Скачать',
                systemRequirements: 'Системные требования: Windows, Linux, MacOS | 400MB HDD | 4GB RAM | 1.3Ghz CPU'
            }
        },
        // Categories
        categories: {
            personalDataNumbers: 'Персональные данные (числа)',
            personalDataText: 'Персональные данные (текст)',
            pciDss: 'PCI DSS',
            bankingSecrecy: 'Банковская тайна',
            itAssets: 'IT-активы',
            customSignatures: 'Пользовательские сигнатуры',
            customSignaturesDesc: 'Можно добавить пользовательские сигнатуры поиска данных, используя обычный текст:',
            customSignaturesOr: 'или любой другой.',
            customSignaturesExamples: ['Secret', 'Password', 'Central bank']
        },
        // IT Assets data
        itAssets: [
            { type: 'IPv4', example: '192.168.1.1' },
            { type: 'IPv6', example: '2001:db8::1' },
            { type: 'Файлы исходного кода', example: 'Находит файлы с исходным кодом. Исходный код должен быть размещен в git репозитории.' },
            { type: 'TLS сертификаты', example: 'Находит папки с наибольшим количеством TLS сертификатов' },
            { type: 'Хеш-данные', example: 'SHA-256, MD5, NTLM (NT hash), SHA-1, SHA-512' }
        ],
        // Table headers
        tableHeaders: {
            dataType: 'Тип данных',
            localName: 'Локальное название',
            country: 'Страна',
            example: 'Пример',
            fileType: 'Тип файла',
            fileFormat: 'Формат файла',
            connector: 'Коннектор',
            description: 'Описание'
        },
        // Features
        features: {
            ranking: {
                title: 'Ранжирование',
                description: 'Сканер показывает файлы с высокой ценностью первыми'
            },
            history: {
                title: 'Просмотр истории сканирования',
                description: 'Отслеживайте все ваши предыдущие сканирования'
            },
            export: {
                title: 'Экспорт результатов',
                description: 'Скачайте результаты в CSV файл'
            },
            schedule: {
                title: 'Планирование сканирований',
                description: 'Автоматизируйте процесс сканирования'
            },
            matchers: {
                title: 'Настраиваемые матчеры',
                description: 'Настройте PII, PCI DSS и другие матчеры'
            },
            formats: {
                title: 'Множество форматов файлов',
                description: 'Настройте форматы файлов (pdf, excel и т.д.)'
            }
        },
        // Footer
        footer: {
            copyright: '© 2025, от admin@angryscan.org'
        },
        // Empty message
        emptyMessage: 'Нет данных для выбранной страны'
    }
};

// Language codes for Google Translate
const GOOGLE_TRANSLATE_LANGUAGES = {
    es: 'es', // Spanish
    de: 'de', // German
    fr: 'fr'  // French
};

// Export
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { I18N, GOOGLE_TRANSLATE_LANGUAGES };
}

