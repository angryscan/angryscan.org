/**
 * Configuration file for Angry Data Scanner website
 * Contains all data structures used throughout the site
 */

const CONFIG = {
    // Site metadata
    site: {
        title: 'Angry Data Scanner - Sensitive Data Discovery Tool',
        description: 'Free open source sensitive data discovery tool',
        githubUrl: 'https://github.com/angryscan/angrydata-app',
        email: 'admin@angryscan.org'
    },

    // Hero section data
    hero: {
        badge: 'Free Open Source',
        title: 'Sensitive Data Discovery Tool',
        description: 'Angry Data Scanner uses pattern matching to automatically discover sensitive data stored in folders, web pages, S3, and databases. It helps organizations identify where sensitive data such as personally identifiable information (PII) and intellectual property is stored.',
        features: [
            'Simple user interface',
            'Sensitive data discovered with 2 clicks',
            'No admin rights required',
            'Works on Linux, Mac, and Windows'
        ],
        cta: {
            primary: {
                text: 'Download Now',
                href: '#download'
            },
            secondary: {
                text: 'View on GitHub',
                href: 'https://github.com/angryscan/angrydata-app',
                external: true
            }
        }
    },

    // Navigation items
    navigation: [
        { text: 'Data Discovery', href: '#discovery' },
        { text: 'Features', href: '#features' },
        { text: 'Download', href: '#download' },
        { text: 'GitHub', href: 'https://github.com/angryscan/angrydata-app', external: true }
    ],

    // Personal data (numbers) table
    personalDataNumbers: [
        { type: 'Phone number', localName: '-', country: 'RU', example: '+7 926 3847291' },
        { type: 'Phone number', localName: '-', country: 'US', example: '+1 212 5550198' },
        { type: 'Taxpayer number', localName: 'ИНН', country: 'RU', example: '7707083893' },
        { type: 'Taxpayer number', localName: 'SSN', country: 'US', example: '536-90-4399' },
        { type: 'Taxpayer number', localName: 'RIN', country: 'CN', example: '110101199003078912' },
        { type: 'Passport', localName: '-', country: 'RU', example: '4505 857555' },
        { type: 'Passport', localName: '-', country: 'US', example: '847293641' },
        { type: 'Pension insurance number', localName: 'СНИЛС', country: 'RU', example: '234-567-890 12' },
        { type: 'Medical insurance number', localName: 'ОМС', country: 'RU', example: '9876543210987654' },
        { type: 'Medical insurance number', localName: 'Medicare', country: 'US', example: '1A2B3C4D5E' },
        { type: 'Car insurance number', localName: 'полис ОСАГО', country: 'RU', example: 'ААА3847291847' },
        { type: 'Driver license', localName: 'Водительские права', country: 'RU', example: '77АВ987654' },
        { type: 'Military ID', localName: 'Удостоверение личности военнослужащего', country: 'RU', example: '3847291847' },
        { type: 'Birthday', localName: '-', country: '-', example: '15.03.1985' },
        { type: 'VIN', localName: '-', country: '-', example: '1HGBH41JXMN109186' }
    ],

    // Personal data (text) table
    personalDataText: [
        { type: 'Full name', localName: 'ФИО', country: 'RU', example: 'Иван Иванович Иванов' },
        { type: 'Full name', localName: 'Full name', country: 'US', example: 'John Smith' },
        { type: 'E-mail', localName: '-', country: '-', example: 'captainbull@gmail.com' },
        { type: 'Address', localName: 'Адрес', country: 'RU', example: 'Москва, ул. Ленина, д. 1' },
        { type: 'Login', localName: '-', country: '-', example: 'username' },
        { type: 'Password', localName: '-', country: '-', example: 'password123' }
    ],

    // PCI DSS data
    pciDss: [
        { type: 'Payment card number', example: '4400 5678 9012 3456' },
        { type: 'CVV', example: '456' }
    ],

    // Banking secrecy data
    bankingSecrecy: [
        { type: 'Bank account (Individual)', country: 'RU', example: '408 028 103 3 5300 5405 83' },
        { type: 'Bank account (Legal entity)', country: 'RU', example: '407 028 103 3 5300 5405 83' }
    ],

    // IT Assets data
    itAssets: [
        { type: 'IPv4', example: '192.168.1.1' },
        { type: 'IPv6', example: '2001:db8::1' },
        { type: 'Source code files', example: 'Finds files with source-code. Source code should be placed in git repository.' },
        { type: 'TLS certificates', example: 'Finds folders with the most amount of TLS certificates' },
        { type: 'Hash data', example: 'SHA-256, MD5, NTLM (NT hash), SHA-1, SHA-512' }
    ],

    // Crypto data
    crypto: [
        { type: 'Crypto wallet', example: '1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa' },
        { type: 'Crypto seed phrase', example: 'A sequence of 12 to 24 words from the BIP39 standard wordlist, used for cryptographic wallet recovery and key derivation' }
    ],

    // Custom signatures description
    customSignatures: {
        description: 'It is possible to add custom data search signatures using plain text:',
        examples: ['Secret', 'Password', 'Central bank']
    },

    // Supported file types
    fileTypes: [
        { category: 'MS Office (tables)', formats: '.xlsx .xls' },
        { category: 'MS Office (text)', formats: '.docx .doc' },
        { category: 'MS Office (presentation)', formats: '.pptx .potx .ppsx .pptm .ppt .pps .pot' },
        { category: 'Open Office (tables)', formats: '.ods' },
        { category: 'Open Office (text)', formats: '.odt' },
        { category: 'Open Office (presentation)', formats: '.odp .otp' },
        { category: 'Adobe', formats: '.pdf' },
        { category: 'Archives', formats: '.zip .rar' },
        { category: 'Plain text', formats: '.txt .csv .xml .json .log' }
    ],

    // Supported data sources
    dataSources: [
        { connector: 'Network Folder', description: 'Scans files on remote directory like Windows environment' },
        { connector: 'HDD/SDD', description: 'Scan local hard drive' },
        { connector: 'S3', description: 'Scan files in S3' },
        { connector: 'HTTP/HTTPS', description: 'Scans web site content' }
    ],

    // Key features
    features: [
        {
            title: 'Ranking',
            description: 'Scanner shows high-value files first',
            icon: 'check'
        },
        {
            title: 'View scanning history',
            description: 'Track all your previous scans',
            icon: 'history'
        },
        {
            title: 'Export results',
            description: 'Download results in a CSV file',
            icon: 'download'
        },
        {
            title: 'Schedule scans',
            description: 'Automate your scanning process',
            icon: 'clock'
        },
        {
            title: 'Configurable matchers',
            description: 'Configure PII, PCI DSS and other matchers',
            icon: 'settings'
        },
        {
            title: 'Multiple file formats',
            description: 'Configure file formats (pdf, excel, etc.)',
            icon: 'file'
        }
    ],

    // Use cases
    useCases: [
        'A leak hunting team scans network folder and ensure that it does not contain source code',
        'An employee finds and deletes files containing card numbers to comply with PCI DSS',
        'A banking employee scans network folder to ensure that it does not contain PII of VIP clients',
        'A boss scans a shared folder of the sales team so they don\'t have client contacts there',
        'Law enforcements need to discover a traces of cryptocurrency on a laptop',
        'A cybersecurity officer need to validate that the database does not contain a personal data'
    ],

    // Download links
    downloads: {
        windows: [
            {
                text: 'Setup x64',
                href: 'https://github.com/angryscan/angrydata-app/releases/latest/download/angry-data-scanner.exe'
            },
            {
                text: 'Portable x64',
                href: 'https://github.com/angryscan/angrydata-app/releases/latest/download/angry-data-scanner-1.4.2-windows-amd64.zip'
            }
        ],
        linux: [
            {
                text: 'DEB x64',
                href: 'https://github.com/angryscan/angrydata-app/releases/latest/download/angry-data-scanner_1.4.2_amd64.deb'
            },
            {
                text: 'Portable x64',
                href: 'https://github.com/angryscan/angrydata-app/releases/latest/download/angry-data-scanner-1.4.2-linux-amd64.tar.gz'
            }
        ],
        macos: [
            {
                text: 'macOS x64',
                href: 'https://github.com/angryscan/angrydata-app/releases/latest/download/angry-data-scanner-1.4.2-mac-amd64.zip'
            },
            {
                text: 'macOS ARM64',
                href: 'https://github.com/angryscan/angrydata-app/releases/latest/download/angry-data-scanner-1.4.2-mac-aarch64.zip'
            }
        ]
    },

    // System requirements
    systemRequirements: 'Windows, Linux, MacOS | 400MB HDD | 4GB RAM | 1.3Ghz CPU'
};

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = CONFIG;
}

