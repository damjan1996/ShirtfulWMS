"""
Datenbank-Konfiguration für Shirtful WMS
Einstellungen für MSSQL Server Verbindung.
"""

import os
from typing import Dict, Any

# Umgebungsvariablen für sensitive Daten
DB_SERVER = os.environ.get('SHIRTFUL_DB_SERVER', 'localhost')
DB_NAME = os.environ.get('SHIRTFUL_DB_NAME', 'ShirtfulWMS')
DB_USER = os.environ.get('SHIRTFUL_DB_USER', '')
DB_PASSWORD = os.environ.get('SHIRTFUL_DB_PASSWORD', '')

# Hauptkonfiguration
DB_CONFIG: Dict[str, Any] = {
    # === Verbindungseinstellungen ===
    'server': DB_SERVER,
    'database': DB_NAME,
    'trusted_connection': True,  # Windows-Authentifizierung
    'username': DB_USER,
    'password': DB_PASSWORD,

    # === Verbindungsoptionen ===
    'connection_timeout': 30,  # Sekunden
    'command_timeout': 300,  # Sekunden (5 Minuten)
    'login_timeout': 10,  # Sekunden

    # === Connection Pool ===
    'pooling': True,
    'min_pool_size': 1,
    'max_pool_size': 10,
    'pool_timeout': 30,

    # === Erweiterte Optionen ===
    'encrypt': False,  # SSL-Verschlüsselung
    'trust_server_certificate': True,
    'multi_subnet_failover': False,
    'application_name': 'ShirtfulWMS',
    'workstation_id': os.environ.get('COMPUTERNAME', 'Unknown'),

    # === Retry-Logik ===
    'retry_enabled': True,
    'retry_count': 3,
    'retry_delay': 1,  # Sekunden

    # === Logging ===
    'log_queries': False,  # SQL-Queries loggen
    'log_slow_queries': True,  # Langsame Queries loggen
    'slow_query_threshold': 5,  # Sekunden
}

# Entwicklungs-Konfiguration
DB_CONFIG_DEV: Dict[str, Any] = {
    **DB_CONFIG,
    'server': 'localhost\\SQLEXPRESS',
    'database': 'ShirtfulWMS_Dev',
    'log_queries': True,
}

# Test-Konfiguration
DB_CONFIG_TEST: Dict[str, Any] = {
    **DB_CONFIG,
    'server': 'localhost\\SQLEXPRESS',
    'database': 'ShirtfulWMS_Test',
    'log_queries': True,
    'pooling': False,  # Kein Pooling für Tests
}

# Produktions-Konfiguration
DB_CONFIG_PROD: Dict[str, Any] = {
    **DB_CONFIG,
    'server': 'SQLSERVER01',
    'database': 'ShirtfulWMS',
    'trusted_connection': False,
    'username': DB_USER,
    'password': DB_PASSWORD,
    'encrypt': True,
    'log_queries': False,
    'max_pool_size': 20,
}

# === SQL-Queries ===

# Tabellen-Erstellung
CREATE_TABLES_SQL = """
-- Mitarbeiter-Tabelle
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Employees' AND xtype='U')
BEGIN
    CREATE TABLE Employees (
        EmployeeID INT IDENTITY(1,1) PRIMARY KEY,
        RFIDTag VARCHAR(50) UNIQUE NOT NULL,
        Name NVARCHAR(100) NOT NULL,
        Department NVARCHAR(50),
        Role NVARCHAR(50),
        Language CHAR(2) DEFAULT 'de',
        IsActive BIT DEFAULT 1,
        CreatedAt DATETIME DEFAULT GETDATE(),
        UpdatedAt DATETIME DEFAULT GETDATE()
    );

    CREATE INDEX IX_Employees_RFID ON Employees(RFIDTag);
END

-- Lieferungen-Tabelle
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Deliveries' AND xtype='U')
BEGIN
    CREATE TABLE Deliveries (
        DeliveryID INT IDENTITY(1,1) PRIMARY KEY,
        Supplier NVARCHAR(100) NOT NULL,
        DeliveryNote NVARCHAR(50),
        ExpectedPackages INT DEFAULT 0,
        ReceivedPackages INT DEFAULT 0,
        ReceivedBy INT FOREIGN KEY REFERENCES Employees(EmployeeID),
        ReceivedAt DATETIME DEFAULT GETDATE(),
        CompletedAt DATETIME,
        Status NVARCHAR(50) DEFAULT 'Offen',
        Notes NVARCHAR(500)
    );

    CREATE INDEX IX_Deliveries_Date ON Deliveries(ReceivedAt);
END

-- Pakete-Tabelle
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Packages' AND xtype='U')
BEGIN
    CREATE TABLE Packages (
        PackageID INT IDENTITY(1,1) PRIMARY KEY,
        QRCode VARCHAR(50) UNIQUE NOT NULL,
        OrderID VARCHAR(50) NOT NULL,
        CustomerName NVARCHAR(100) NOT NULL,
        ItemCount INT DEFAULT 1,
        Priority NVARCHAR(20) DEFAULT 'Normal',
        CurrentStage NVARCHAR(50) DEFAULT 'Wareneingang',
        DeliveryID INT FOREIGN KEY REFERENCES Deliveries(DeliveryID),
        CreatedBy INT FOREIGN KEY REFERENCES Employees(EmployeeID),
        CreatedAt DATETIME DEFAULT GETDATE(),
        LastUpdate DATETIME DEFAULT GETDATE(),
        LastUpdatedBy INT FOREIGN KEY REFERENCES Employees(EmployeeID),
        Notes NVARCHAR(500),

        -- Qualitätskontrolle
        QualityStatus NVARCHAR(20),
        QualityCheckedBy INT FOREIGN KEY REFERENCES Employees(EmployeeID),
        QualityCheckDate DATETIME,

        -- Versand
        ShippingMethod NVARCHAR(50),
        TrackingNumber VARCHAR(50),
        ShippedBy INT FOREIGN KEY REFERENCES Employees(EmployeeID),
        ShippedAt DATETIME
    );

    CREATE INDEX IX_Packages_QR ON Packages(QRCode);
    CREATE INDEX IX_Packages_Order ON Packages(OrderID);
    CREATE INDEX IX_Packages_Stage ON Packages(CurrentStage);
    CREATE INDEX IX_Packages_Created ON Packages(CreatedAt);
END

-- Paket-Historie
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='PackageHistory' AND xtype='U')
BEGIN
    CREATE TABLE PackageHistory (
        HistoryID INT IDENTITY(1,1) PRIMARY KEY,
        PackageID INT FOREIGN KEY REFERENCES Packages(PackageID),
        Stage NVARCHAR(50) NOT NULL,
        EmployeeID INT FOREIGN KEY REFERENCES Employees(EmployeeID),
        Timestamp DATETIME DEFAULT GETDATE(),
        Notes NVARCHAR(500)
    );

    CREATE INDEX IX_History_Package ON PackageHistory(PackageID);
    CREATE INDEX IX_History_Time ON PackageHistory(Timestamp);
END

-- Zeiterfassung
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TimeTracking' AND xtype='U')
BEGIN
    CREATE TABLE TimeTracking (
        EntryID INT IDENTITY(1,1) PRIMARY KEY,
        EmployeeID INT FOREIGN KEY REFERENCES Employees(EmployeeID),
        ClockIn DATETIME NOT NULL,
        ClockOut DATETIME,
        BreakMinutes INT DEFAULT 0,
        TotalMinutes AS DATEDIFF(MINUTE, ClockIn, ISNULL(ClockOut, GETDATE())) - BreakMinutes
    );

    CREATE INDEX IX_Time_Employee ON TimeTracking(EmployeeID);
    CREATE INDEX IX_Time_Date ON TimeTracking(ClockIn);
END

-- Qualitätsprobleme
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='QualityIssues' AND xtype='U')
BEGIN
    CREATE TABLE QualityIssues (
        IssueID INT IDENTITY(1,1) PRIMARY KEY,
        PackageID INT FOREIGN KEY REFERENCES Packages(PackageID),
        IssueType NVARCHAR(100),
        Description NVARCHAR(500),
        ReportedBy INT FOREIGN KEY REFERENCES Employees(EmployeeID),
        ReportedAt DATETIME DEFAULT GETDATE(),
        ResolvedBy INT FOREIGN KEY REFERENCES Employees(EmployeeID),
        ResolvedAt DATETIME,
        Resolution NVARCHAR(500)
    );

    CREATE INDEX IX_Issues_Package ON QualityIssues(PackageID);
END

-- System-Einstellungen
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Settings' AND xtype='U')
BEGIN
    CREATE TABLE Settings (
        SettingID INT IDENTITY(1,1) PRIMARY KEY,
        Category NVARCHAR(50) NOT NULL,
        Name NVARCHAR(50) NOT NULL,
        Value NVARCHAR(500),
        DataType NVARCHAR(20) DEFAULT 'string',
        UpdatedBy INT FOREIGN KEY REFERENCES Employees(EmployeeID),
        UpdatedAt DATETIME DEFAULT GETDATE(),
        CONSTRAINT UQ_Settings UNIQUE(Category, Name)
    );
END

-- Audit-Log
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='AuditLog' AND xtype='U')
BEGIN
    CREATE TABLE AuditLog (
        LogID INT IDENTITY(1,1) PRIMARY KEY,
        TableName NVARCHAR(50),
        RecordID INT,
        Action NVARCHAR(20),
        OldValue NVARCHAR(MAX),
        NewValue NVARCHAR(MAX),
        ChangedBy INT FOREIGN KEY REFERENCES Employees(EmployeeID),
        ChangedAt DATETIME DEFAULT GETDATE()
    );

    CREATE INDEX IX_Audit_Table ON AuditLog(TableName);
    CREATE INDEX IX_Audit_Date ON AuditLog(ChangedAt);
END
"""

# Standard-Daten
INSERT_DEFAULT_DATA_SQL = """
-- Standard-Mitarbeiter
IF NOT EXISTS (SELECT * FROM Employees WHERE RFIDTag = 'ADMIN001')
BEGIN
    INSERT INTO Employees (RFIDTag, Name, Department, Role, Language)
    VALUES 
        ('ADMIN001', 'Administrator', 'IT', 'Administrator', 'de'),
        ('TEST0001', 'Test User', 'Lager', 'Lagerarbeiter', 'de');
END

-- Standard-Einstellungen
IF NOT EXISTS (SELECT * FROM Settings WHERE Category = 'System' AND Name = 'Version')
BEGIN
    INSERT INTO Settings (Category, Name, Value, DataType)
    VALUES 
        ('System', 'Version', '1.0.0', 'string'),
        ('System', 'InstallDate', CONVERT(VARCHAR, GETDATE(), 120), 'datetime'),
        ('Business', 'WorkStartTime', '06:00', 'time'),
        ('Business', 'WorkEndTime', '22:00', 'time'),
        ('Business', 'BreakAfterHours', '6', 'int'),
        ('Business', 'BreakDurationMinutes', '30', 'int');
END
"""

# Views
CREATE_VIEWS_SQL = """
-- Aktuelle Pakete Übersicht
IF EXISTS (SELECT * FROM sysobjects WHERE name='vw_CurrentPackages' AND xtype='V')
    DROP VIEW vw_CurrentPackages
GO

CREATE VIEW vw_CurrentPackages AS
SELECT 
    p.PackageID,
    p.QRCode,
    p.OrderID,
    p.CustomerName,
    p.ItemCount,
    p.Priority,
    p.CurrentStage,
    p.CreatedAt,
    p.LastUpdate,
    e1.Name AS CreatedByName,
    e2.Name AS LastUpdatedByName,
    d.Supplier,
    d.DeliveryNote
FROM Packages p
LEFT JOIN Employees e1 ON p.CreatedBy = e1.EmployeeID
LEFT JOIN Employees e2 ON p.LastUpdatedBy = e2.EmployeeID
LEFT JOIN Deliveries d ON p.DeliveryID = d.DeliveryID
WHERE p.CurrentStage != 'Versendet'
GO

-- Tagesstatistik
IF EXISTS (SELECT * FROM sysobjects WHERE name='vw_DailyStatistics' AND xtype='V')
    DROP VIEW vw_DailyStatistics
GO

CREATE VIEW vw_DailyStatistics AS
SELECT 
    CAST(p.CreatedAt AS DATE) AS Date,
    COUNT(*) AS TotalPackages,
    SUM(CASE WHEN p.CurrentStage = 'Wareneingang' THEN 1 ELSE 0 END) AS InReceiving,
    SUM(CASE WHEN p.CurrentStage = 'In Veredelung' THEN 1 ELSE 0 END) AS InProcessing,
    SUM(CASE WHEN p.CurrentStage = 'In Betuchung' THEN 1 ELSE 0 END) AS InFabric,
    SUM(CASE WHEN p.CurrentStage = 'Qualitätskontrolle' THEN 1 ELSE 0 END) AS InQuality,
    SUM(CASE WHEN p.CurrentStage = 'Versandbereit' THEN 1 ELSE 0 END) AS ReadyToShip,
    SUM(CASE WHEN p.CurrentStage = 'Versendet' THEN 1 ELSE 0 END) AS Shipped
FROM Packages p
GROUP BY CAST(p.CreatedAt AS DATE)
GO

-- Mitarbeiter-Performance
IF EXISTS (SELECT * FROM sysobjects WHERE name='vw_EmployeePerformance' AND xtype='V')
    DROP VIEW vw_EmployeePerformance
GO

CREATE VIEW vw_EmployeePerformance AS
SELECT 
    e.EmployeeID,
    e.Name,
    e.Department,
    COUNT(DISTINCT ph.PackageID) AS PackagesProcessed,
    COUNT(DISTINCT CAST(ph.Timestamp AS DATE)) AS DaysWorked,
    AVG(DATEDIFF(MINUTE, ph1.Timestamp, ph2.Timestamp)) AS AvgProcessingTime
FROM Employees e
LEFT JOIN PackageHistory ph ON e.EmployeeID = ph.EmployeeID
LEFT JOIN PackageHistory ph1 ON ph.PackageID = ph1.PackageID AND ph1.Stage = 'Wareneingang'
LEFT JOIN PackageHistory ph2 ON ph.PackageID = ph2.PackageID AND ph2.Stage = 'Versendet'
WHERE e.IsActive = 1
GROUP BY e.EmployeeID, e.Name, e.Department
GO
"""

# Stored Procedures
CREATE_PROCEDURES_SQL = """
-- Paket-Status Update
IF EXISTS (SELECT * FROM sysobjects WHERE name='sp_UpdatePackageStatus' AND xtype='P')
    DROP PROCEDURE sp_UpdatePackageStatus
GO

CREATE PROCEDURE sp_UpdatePackageStatus
    @PackageID INT,
    @NewStatus NVARCHAR(50),
    @EmployeeID INT,
    @Notes NVARCHAR(500) = NULL
AS
BEGIN
    SET NOCOUNT ON;

    BEGIN TRANSACTION;

    -- Update Package
    UPDATE Packages
    SET CurrentStage = @NewStatus,
        LastUpdate = GETDATE(),
        LastUpdatedBy = @EmployeeID
    WHERE PackageID = @PackageID;

    -- Insert History
    INSERT INTO PackageHistory (PackageID, Stage, EmployeeID, Notes)
    VALUES (@PackageID, @NewStatus, @EmployeeID, @Notes);

    COMMIT TRANSACTION;

    SELECT @@ROWCOUNT AS RowsAffected;
END
GO

-- Tagesabschluss
IF EXISTS (SELECT * FROM sysobjects WHERE name='sp_DailyCloseout' AND xtype='P')
    DROP PROCEDURE sp_DailyCloseout
GO

CREATE PROCEDURE sp_DailyCloseout
    @Date DATE = NULL
AS
BEGIN
    SET NOCOUNT ON;

    IF @Date IS NULL
        SET @Date = CAST(GETDATE() AS DATE);

    SELECT 
        'Packages Received' AS Metric,
        COUNT(*) AS Count
    FROM Packages
    WHERE CAST(CreatedAt AS DATE) = @Date

    UNION ALL

    SELECT 
        'Packages Shipped' AS Metric,
        COUNT(*) AS Count
    FROM Packages
    WHERE CAST(ShippedAt AS DATE) = @Date

    UNION ALL

    SELECT 
        'Quality Issues' AS Metric,
        COUNT(*) AS Count
    FROM QualityIssues
    WHERE CAST(ReportedAt AS DATE) = @Date

    UNION ALL

    SELECT 
        'Employees Active' AS Metric,
        COUNT(DISTINCT EmployeeID) AS Count
    FROM TimeTracking
    WHERE CAST(ClockIn AS DATE) = @Date;
END
GO
"""


def get_connection_string(environment: str = 'default') -> str:
    """
    Gibt den Connection String für die gewünschte Umgebung zurück.

    Args:
        environment: 'default', 'dev', 'test' oder 'prod'

    Returns:
        ODBC Connection String
    """
    configs = {
        'default': DB_CONFIG,
        'dev': DB_CONFIG_DEV,
        'test': DB_CONFIG_TEST,
        'prod': DB_CONFIG_PROD
    }

    config = configs.get(environment, DB_CONFIG)

    # Connection String bauen
    parts = [
        f"DRIVER={{ODBC Driver 17 for SQL Server}}",
        f"SERVER={config['server']}",
        f"DATABASE={config['database']}"
    ]

    if config.get('trusted_connection'):
        parts.append("Trusted_Connection=yes")
    else:
        parts.extend([
            f"UID={config['username']}",
            f"PWD={config['password']}"
        ])

    # Weitere Optionen
    if config.get('encrypt'):
        parts.append("Encrypt=yes")
    if config.get('trust_server_certificate'):
        parts.append("TrustServerCertificate=yes")
    if config.get('application_name'):
        parts.append(f"APP={config['application_name']}")
    if config.get('connection_timeout'):
        parts.append(f"Connection Timeout={config['connection_timeout']}")

    return ';'.join(parts)


# Test
if __name__ == "__main__":
    print("=== Shirtful WMS Database Configuration ===\n")

    # Connection Strings anzeigen
    for env in ['default', 'dev', 'test', 'prod']:
        print(f"{env.upper()}:")
        print(f"  {get_connection_string(env)}\n")

    # Config-Details
    print("Default Configuration:")
    for key, value in DB_CONFIG.items():
        if key not in ['password']:  # Passwort nicht anzeigen
            print(f"  {key}: {value}")