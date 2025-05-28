-- =============================================
-- Shirtful WMS - Datenbank Schema
-- Version: 1.0.0
-- Datum: 2024-05
-- =============================================

-- Datenbank erstellen (falls nicht vorhanden)
IF NOT EXISTS (SELECT * FROM sys.databases WHERE name = 'ShirtfulWMS')
BEGIN
    CREATE DATABASE ShirtfulWMS;
END
GO

USE ShirtfulWMS;
GO

-- =============================================
-- Tabellen löschen (für Neuinstallation)
-- =============================================
/*
DROP TABLE IF EXISTS AuditLog;
DROP TABLE IF EXISTS QualityIssues;
DROP TABLE IF EXISTS TimeTracking;
DROP TABLE IF EXISTS PackageHistory;
DROP TABLE IF EXISTS Packages;
DROP TABLE IF EXISTS Deliveries;
DROP TABLE IF EXISTS Settings;
DROP TABLE IF EXISTS Employees;
*/

-- =============================================
-- Mitarbeiter-Tabelle
-- =============================================
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Employees' AND xtype='U')
BEGIN
    CREATE TABLE Employees (
        EmployeeID INT IDENTITY(1,1) PRIMARY KEY,
        RFIDTag VARCHAR(50) UNIQUE NOT NULL,
        Name NVARCHAR(100) NOT NULL,
        Department NVARCHAR(50),
        Role NVARCHAR(50),
        Language CHAR(2) DEFAULT 'de',
        Email NVARCHAR(100),
        Phone NVARCHAR(50),
        IsActive BIT DEFAULT 1,
        CreatedAt DATETIME DEFAULT GETDATE(),
        UpdatedAt DATETIME DEFAULT GETDATE(),
        LastLogin DATETIME,
        LoginCount INT DEFAULT 0
    );

    CREATE INDEX IX_Employees_RFID ON Employees(RFIDTag);
    CREATE INDEX IX_Employees_Active ON Employees(IsActive);

    PRINT 'Tabelle Employees erstellt';
END
GO

-- =============================================
-- Lieferungen-Tabelle
-- =============================================
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
    CREATE INDEX IX_Deliveries_Status ON Deliveries(Status);

    PRINT 'Tabelle Deliveries erstellt';
END
GO

-- =============================================
-- Pakete-Tabelle
-- =============================================
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

        -- Erstellung
        CreatedBy INT FOREIGN KEY REFERENCES Employees(EmployeeID),
        CreatedAt DATETIME DEFAULT GETDATE(),

        -- Letzte Änderung
        LastUpdate DATETIME DEFAULT GETDATE(),
        LastUpdatedBy INT FOREIGN KEY REFERENCES Employees(EmployeeID),

        -- Veredelung
        ProcessingType NVARCHAR(50),
        ProcessingStarted DATETIME,
        ProcessingCompleted DATETIME,
        ProcessingBy INT FOREIGN KEY REFERENCES Employees(EmployeeID),

        -- Betuchung
        FabricStarted DATETIME,
        FabricCompleted DATETIME,
        FabricBy INT FOREIGN KEY REFERENCES Employees(EmployeeID),

        -- Qualitätskontrolle
        QualityStatus NVARCHAR(20),
        QualityCheckedBy INT FOREIGN KEY REFERENCES Employees(EmployeeID),
        QualityCheckDate DATETIME,

        -- Versand
        ShippingMethod NVARCHAR(50),
        TrackingNumber VARCHAR(50),
        ShippedBy INT FOREIGN KEY REFERENCES Employees(EmployeeID),
        ShippedAt DATETIME,

        -- Zusätzliche Felder
        Notes NVARCHAR(500),
        CustomField1 NVARCHAR(100),
        CustomField2 NVARCHAR(100),
        CustomField3 NVARCHAR(100)
    );

    CREATE INDEX IX_Packages_QR ON Packages(QRCode);
    CREATE INDEX IX_Packages_Order ON Packages(OrderID);
    CREATE INDEX IX_Packages_Customer ON Packages(CustomerName);
    CREATE INDEX IX_Packages_Stage ON Packages(CurrentStage);
    CREATE INDEX IX_Packages_Created ON Packages(CreatedAt);
    CREATE INDEX IX_Packages_Priority ON Packages(Priority);

    PRINT 'Tabelle Packages erstellt';
END
GO

-- =============================================
-- Paket-Historie
-- =============================================
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='PackageHistory' AND xtype='U')
BEGIN
    CREATE TABLE PackageHistory (
        HistoryID INT IDENTITY(1,1) PRIMARY KEY,
        PackageID INT FOREIGN KEY REFERENCES Packages(PackageID) ON DELETE CASCADE,
        Stage NVARCHAR(50) NOT NULL,
        Action NVARCHAR(50),
        EmployeeID INT FOREIGN KEY REFERENCES Employees(EmployeeID),
        Timestamp DATETIME DEFAULT GETDATE(),
        Duration INT, -- Minuten in dieser Stage
        Notes NVARCHAR(500),
        OldValue NVARCHAR(200),
        NewValue NVARCHAR(200)
    );

    CREATE INDEX IX_History_Package ON PackageHistory(PackageID);
    CREATE INDEX IX_History_Time ON PackageHistory(Timestamp);
    CREATE INDEX IX_History_Employee ON PackageHistory(EmployeeID);

    PRINT 'Tabelle PackageHistory erstellt';
END
GO

-- =============================================
-- Zeiterfassung
-- =============================================
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TimeTracking' AND xtype='U')
BEGIN
    CREATE TABLE TimeTracking (
        EntryID INT IDENTITY(1,1) PRIMARY KEY,
        EmployeeID INT FOREIGN KEY REFERENCES Employees(EmployeeID),
        ClockIn DATETIME NOT NULL,
        ClockOut DATETIME,
        BreakStart DATETIME,
        BreakEnd DATETIME,
        BreakMinutes INT DEFAULT 0,
        WorkMinutes AS DATEDIFF(MINUTE, ClockIn, ISNULL(ClockOut, GETDATE())) - ISNULL(BreakMinutes, 0),
        Station NVARCHAR(50),
        Notes NVARCHAR(200)
    );

    CREATE INDEX IX_Time_Employee ON TimeTracking(EmployeeID);
    CREATE INDEX IX_Time_Date ON TimeTracking(ClockIn);

    PRINT 'Tabelle TimeTracking erstellt';
END
GO

-- =============================================
-- Qualitätsprobleme
-- =============================================
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='QualityIssues' AND xtype='U')
BEGIN
    CREATE TABLE QualityIssues (
        IssueID INT IDENTITY(1,1) PRIMARY KEY,
        PackageID INT FOREIGN KEY REFERENCES Packages(PackageID) ON DELETE CASCADE,
        IssueType NVARCHAR(100),
        Severity NVARCHAR(20) DEFAULT 'Medium', -- Low, Medium, High, Critical
        Description NVARCHAR(500),
        ReportedBy INT FOREIGN KEY REFERENCES Employees(EmployeeID),
        ReportedAt DATETIME DEFAULT GETDATE(),
        ResolvedBy INT FOREIGN KEY REFERENCES Employees(EmployeeID),
        ResolvedAt DATETIME,
        Resolution NVARCHAR(500),
        PreventiveAction NVARCHAR(500),
        Cost DECIMAL(10,2)
    );

    CREATE INDEX IX_Issues_Package ON QualityIssues(PackageID);
    CREATE INDEX IX_Issues_Date ON QualityIssues(ReportedAt);
    CREATE INDEX IX_Issues_Type ON QualityIssues(IssueType);

    PRINT 'Tabelle QualityIssues erstellt';
END
GO

-- =============================================
-- System-Einstellungen
-- =============================================
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Settings' AND xtype='U')
BEGIN
    CREATE TABLE Settings (
        SettingID INT IDENTITY(1,1) PRIMARY KEY,
        Category NVARCHAR(50) NOT NULL,
        Name NVARCHAR(50) NOT NULL,
        Value NVARCHAR(500),
        DataType NVARCHAR(20) DEFAULT 'string',
        Description NVARCHAR(200),
        UpdatedBy INT FOREIGN KEY REFERENCES Employees(EmployeeID),
        UpdatedAt DATETIME DEFAULT GETDATE(),
        CONSTRAINT UQ_Settings UNIQUE(Category, Name)
    );

    CREATE INDEX IX_Settings_Category ON Settings(Category);

    PRINT 'Tabelle Settings erstellt';
END
GO

-- =============================================
-- Audit-Log
-- =============================================
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='AuditLog' AND xtype='U')
BEGIN
    CREATE TABLE AuditLog (
        LogID INT IDENTITY(1,1) PRIMARY KEY,
        TableName NVARCHAR(50),
        RecordID INT,
        Action NVARCHAR(20), -- INSERT, UPDATE, DELETE
        FieldName NVARCHAR(50),
        OldValue NVARCHAR(MAX),
        NewValue NVARCHAR(MAX),
        ChangedBy INT FOREIGN KEY REFERENCES Employees(EmployeeID),
        ChangedAt DATETIME DEFAULT GETDATE(),
        IPAddress NVARCHAR(50),
        UserAgent NVARCHAR(200)
    );

    CREATE INDEX IX_Audit_Table ON AuditLog(TableName);
    CREATE INDEX IX_Audit_Date ON AuditLog(ChangedAt);
    CREATE INDEX IX_Audit_User ON AuditLog(ChangedBy);

    PRINT 'Tabelle AuditLog erstellt';
END
GO

-- =============================================
-- Views
-- =============================================

-- Aktuelle Pakete Übersicht
IF EXISTS (SELECT * FROM sys.views WHERE name = 'vw_CurrentPackages')
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
    d.DeliveryNote,
    DATEDIFF(HOUR, p.CreatedAt, GETDATE()) AS AgeHours,
    CASE
        WHEN p.Priority = 'Express' THEN 1
        WHEN p.Priority = 'Hoch' THEN 2
        WHEN p.Priority = 'Normal' THEN 3
        ELSE 4
    END AS PriorityOrder
FROM Packages p
LEFT JOIN Employees e1 ON p.CreatedBy = e1.EmployeeID
LEFT JOIN Employees e2 ON p.LastUpdatedBy = e2.EmployeeID
LEFT JOIN Deliveries d ON p.DeliveryID = d.DeliveryID
WHERE p.CurrentStage != 'Versendet'
GO

PRINT 'View vw_CurrentPackages erstellt';
GO

-- Tagesstatistik
IF EXISTS (SELECT * FROM sys.views WHERE name = 'vw_DailyStatistics')
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
    SUM(CASE WHEN p.CurrentStage = 'Qualität OK' THEN 1 ELSE 0 END) AS QualityOK,
    SUM(CASE WHEN p.CurrentStage = 'Nacharbeit erforderlich' THEN 1 ELSE 0 END) AS Rework,
    SUM(CASE WHEN p.CurrentStage = 'Versandbereit' THEN 1 ELSE 0 END) AS ReadyToShip,
    SUM(CASE WHEN p.CurrentStage = 'Versendet' THEN 1 ELSE 0 END) AS Shipped,
    COUNT(DISTINCT p.CustomerName) AS UniqueCustomers,
    COUNT(DISTINCT p.CreatedBy) AS ActiveEmployees
FROM Packages p
GROUP BY CAST(p.CreatedAt AS DATE)
GO

PRINT 'View vw_DailyStatistics erstellt';
GO

-- Mitarbeiter-Performance
IF EXISTS (SELECT * FROM sys.views WHERE name = 'vw_EmployeePerformance')
    DROP VIEW vw_EmployeePerformance
GO

CREATE VIEW vw_EmployeePerformance AS
SELECT
    e.EmployeeID,
    e.Name,
    e.Department,
    e.Role,
    COUNT(DISTINCT ph.PackageID) AS PackagesProcessed,
    COUNT(DISTINCT CAST(ph.Timestamp AS DATE)) AS DaysWorked,
    SUM(CASE WHEN ph.Stage = 'Wareneingang' THEN 1 ELSE 0 END) AS PackagesReceived,
    SUM(CASE WHEN ph.Stage = 'In Veredelung' THEN 1 ELSE 0 END) AS PackagesProcessed_,
    SUM(CASE WHEN ph.Stage = 'Qualität OK' THEN 1 ELSE 0 END) AS QualityChecked,
    SUM(CASE WHEN ph.Stage = 'Versendet' THEN 1 ELSE 0 END) AS PackagesShipped,
    AVG(ph.Duration) AS AvgProcessingMinutes,
    MAX(ph.Timestamp) AS LastActivity
FROM Employees e
LEFT JOIN PackageHistory ph ON e.EmployeeID = ph.EmployeeID
WHERE e.IsActive = 1
GROUP BY e.EmployeeID, e.Name, e.Department, e.Role
GO

PRINT 'View vw_EmployeePerformance erstellt';
GO

-- =============================================
-- Stored Procedures
-- =============================================

-- Paket-Status Update
IF EXISTS (SELECT * FROM sys.procedures WHERE name = 'sp_UpdatePackageStatus')
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

    DECLARE @OldStatus NVARCHAR(50);
    DECLARE @Duration INT;

    BEGIN TRANSACTION;

    -- Alten Status holen
    SELECT @OldStatus = CurrentStage
    FROM Packages
    WHERE PackageID = @PackageID;

    -- Dauer berechnen
    SELECT @Duration = DATEDIFF(MINUTE, MAX(Timestamp), GETDATE())
    FROM PackageHistory
    WHERE PackageID = @PackageID AND Stage = @OldStatus;

    -- Package updaten
    UPDATE Packages
    SET CurrentStage = @NewStatus,
        LastUpdate = GETDATE(),
        LastUpdatedBy = @EmployeeID
    WHERE PackageID = @PackageID;

    -- Historie eintragen
    INSERT INTO PackageHistory (PackageID, Stage, Action, EmployeeID, Duration, Notes, OldValue, NewValue)
    VALUES (@PackageID, @NewStatus, 'STATUS_CHANGE', @EmployeeID, @Duration, @Notes, @OldStatus, @NewStatus);

    -- Spezielle Updates je nach Status
    IF @NewStatus = 'In Veredelung'
        UPDATE Packages SET ProcessingStarted = GETDATE(), ProcessingBy = @EmployeeID WHERE PackageID = @PackageID;
    ELSE IF @NewStatus = 'In Betuchung'
        UPDATE Packages SET FabricStarted = GETDATE(), FabricBy = @EmployeeID WHERE PackageID = @PackageID;
    ELSE IF @NewStatus = 'Versendet'
        UPDATE Packages SET ShippedAt = GETDATE(), ShippedBy = @EmployeeID WHERE PackageID = @PackageID;

    COMMIT TRANSACTION;

    SELECT @@ROWCOUNT AS RowsAffected;
END
GO

PRINT 'Stored Procedure sp_UpdatePackageStatus erstellt';
GO

-- Tagesabschluss
IF EXISTS (SELECT * FROM sys.procedures WHERE name = 'sp_DailyCloseout')
    DROP PROCEDURE sp_DailyCloseout
GO

CREATE PROCEDURE sp_DailyCloseout
    @Date DATE = NULL
AS
BEGIN
    SET NOCOUNT ON;

    IF @Date IS NULL
        SET @Date = CAST(GETDATE() AS DATE);

    -- Zusammenfassung
    SELECT
        'Packages Received' AS Metric,
        COUNT(*) AS Count,
        AVG(ItemCount) AS AvgItems
    FROM Packages
    WHERE CAST(CreatedAt AS DATE) = @Date

    UNION ALL

    SELECT
        'Packages Shipped' AS Metric,
        COUNT(*) AS Count,
        NULL AS AvgItems
    FROM Packages
    WHERE CAST(ShippedAt AS DATE) = @Date

    UNION ALL

    SELECT
        'Quality Issues' AS Metric,
        COUNT(*) AS Count,
        NULL AS AvgItems
    FROM QualityIssues
    WHERE CAST(ReportedAt AS DATE) = @Date

    UNION ALL

    SELECT
        'Employees Active' AS Metric,
        COUNT(DISTINCT EmployeeID) AS Count,
        AVG(WorkMinutes) AS AvgItems
    FROM TimeTracking
    WHERE CAST(ClockIn AS DATE) = @Date;

    -- Top Mitarbeiter
    SELECT TOP 5
        e.Name,
        COUNT(ph.PackageID) AS PackagesProcessed,
        AVG(ph.Duration) AS AvgMinutes
    FROM Employees e
    JOIN PackageHistory ph ON e.EmployeeID = ph.EmployeeID
    WHERE CAST(ph.Timestamp AS DATE) = @Date
    GROUP BY e.EmployeeID, e.Name
    ORDER BY COUNT(ph.PackageID) DESC;

    -- Problematische Pakete
    SELECT
        p.QRCode,
        p.OrderID,
        p.CustomerName,
        p.CurrentStage,
        DATEDIFF(HOUR, p.CreatedAt, GETDATE()) AS AgeHours
    FROM Packages p
    WHERE p.CurrentStage NOT IN ('Versendet', 'Storniert')
    AND DATEDIFF(HOUR, p.CreatedAt, GETDATE()) > 48
    ORDER BY p.CreatedAt;
END
GO

PRINT 'Stored Procedure sp_DailyCloseout erstellt';
GO

-- =============================================
-- Trigger
-- =============================================

-- Audit-Trigger für Packages
IF EXISTS (SELECT * FROM sys.triggers WHERE name = 'tr_Packages_Audit')
    DROP TRIGGER tr_Packages_Audit
GO

CREATE TRIGGER tr_Packages_Audit
ON Packages
AFTER UPDATE
AS
BEGIN
    SET NOCOUNT ON;

    -- Status-Änderungen loggen
    IF UPDATE(CurrentStage)
    BEGIN
        INSERT INTO AuditLog (TableName, RecordID, Action, FieldName, OldValue, NewValue, ChangedBy)
        SELECT
            'Packages',
            i.PackageID,
            'UPDATE',
            'CurrentStage',
            d.CurrentStage,
            i.CurrentStage,
            i.LastUpdatedBy
        FROM inserted i
        INNER JOIN deleted d ON i.PackageID = d.PackageID
        WHERE i.CurrentStage != d.CurrentStage;
    END
END
GO

PRINT 'Trigger tr_Packages_Audit erstellt';
GO

-- =============================================
-- Basis-Daten einfügen
-- =============================================

-- Standard-Mitarbeiter
IF NOT EXISTS (SELECT * FROM Employees WHERE RFIDTag = 'ADMIN001')
BEGIN
    INSERT INTO Employees (RFIDTag, Name, Department, Role, Language, Email)
    VALUES
        ('ADMIN001', 'Administrator', 'IT', 'Administrator', 'de', 'admin@shirtful.de'),
        ('TEST0001', 'Test User', 'Lager', 'Lagerarbeiter', 'de', 'test@shirtful.de'),
        ('12345678', 'Max Mustermann', 'Lager', 'Lagerarbeiter', 'de', 'max@shirtful.de'),
        ('87654321', 'Erika Musterfrau', 'Veredelung', 'Teamleiter', 'de', 'erika@shirtful.de'),
        ('ABCD1234', 'John Doe', 'Qualitätskontrolle', 'Prüfer', 'en', 'john@shirtful.de');

    PRINT 'Standard-Mitarbeiter eingefügt';
END

-- Standard-Einstellungen
IF NOT EXISTS (SELECT * FROM Settings WHERE Category = 'System' AND Name = 'Version')
BEGIN
    INSERT INTO Settings (Category, Name, Value, DataType, Description)
    VALUES
        ('System', 'Version', '1.0.0', 'string', 'System-Version'),
        ('System', 'InstallDate', CONVERT(VARCHAR, GETDATE(), 120), 'datetime', 'Installations-Datum'),
        ('System', 'DatabaseVersion', '1.0', 'string', 'Datenbank-Version'),
        ('Business', 'WorkStartTime', '06:00', 'time', 'Arbeitsbeginn'),
        ('Business', 'WorkEndTime', '22:00', 'time', 'Arbeitsende'),
        ('Business', 'BreakAfterHours', '6', 'int', 'Pause nach X Stunden'),
        ('Business', 'BreakDurationMinutes', '30', 'int', 'Pausendauer in Minuten'),
        ('Process', 'AutoPrintLabels', 'true', 'bool', 'Labels automatisch drucken'),
        ('Process', 'RequireQualityCheck', 'true', 'bool', 'Qualitätskontrolle erforderlich'),
        ('Process', 'MaxBatchSize', '50', 'int', 'Maximale Batch-Größe');

    PRINT 'Standard-Einstellungen eingefügt';
END

-- =============================================
-- Berechtigungen
-- =============================================

-- Rolle für Anwendung erstellen
/*
IF NOT EXISTS (SELECT * FROM sys.database_principals WHERE name = 'ShirtfulWMS_App')
BEGIN
    CREATE ROLE ShirtfulWMS_App;

    -- Berechtigungen vergeben
    GRANT SELECT, INSERT, UPDATE, DELETE ON SCHEMA::dbo TO ShirtfulWMS_App;
    GRANT EXECUTE ON SCHEMA::dbo TO ShirtfulWMS_App;

    PRINT 'Rolle ShirtfulWMS_App erstellt';
END
*/

-- =============================================
-- Fertig
-- =============================================
PRINT '';
PRINT '=============================================';
PRINT 'Shirtful WMS Datenbank-Setup abgeschlossen';
PRINT '=============================================';
PRINT '';
PRINT 'Nächste Schritte:';
PRINT '1. Connection String in config/database_config.py anpassen';
PRINT '2. RFID-Tags für Mitarbeiter in Employees-Tabelle eintragen';
PRINT '3. Anwendungen starten und testen';
PRINT '';
GO