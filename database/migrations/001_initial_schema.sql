-- =============================================
-- Migration: 001_initial_schema.sql
-- Datum: 2024-05-01
-- Beschreibung: Initiales Datenbankschema für Shirtful WMS
-- =============================================

-- Migration-Tracking Tabelle
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='DatabaseMigrations' AND xtype='U')
BEGIN
    CREATE TABLE DatabaseMigrations (
        MigrationID INT IDENTITY(1,1) PRIMARY KEY,
        Version VARCHAR(50) NOT NULL UNIQUE,
        Description NVARCHAR(200),
        AppliedAt DATETIME DEFAULT GETDATE(),
        AppliedBy NVARCHAR(100) DEFAULT SYSTEM_USER
    );
END
GO

-- Prüfen ob Migration bereits angewendet wurde
IF EXISTS (SELECT * FROM DatabaseMigrations WHERE Version = '001_initial_schema')
BEGIN
    PRINT 'Migration 001_initial_schema bereits angewendet. Überspringe...';
    RETURN;
END
GO

-- =============================================
-- Tabellen erstellen
-- =============================================

-- Mitarbeiter
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
GO

-- Lieferungen
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
GO

-- Pakete
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
GO

-- Paket-Historie
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
GO

-- Zeiterfassung
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
GO

-- Qualitätsprobleme
CREATE TABLE QualityIssues (
    IssueID INT IDENTITY(1,1) PRIMARY KEY,
    PackageID INT FOREIGN KEY REFERENCES Packages(PackageID) ON DELETE CASCADE,
    IssueType NVARCHAR(100),
    Severity NVARCHAR(20) DEFAULT 'Medium',
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
GO

-- System-Einstellungen
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
GO

-- Audit-Log
CREATE TABLE AuditLog (
    LogID INT IDENTITY(1,1) PRIMARY KEY,
    TableName NVARCHAR(50),
    RecordID INT,
    Action NVARCHAR(20),
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
GO

-- =============================================
-- Views erstellen
-- =============================================

-- Aktuelle Pakete Übersicht
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
WHERE p.CurrentStage != 'Versendet';
GO

-- =============================================
-- Stored Procedures
-- =============================================

-- Paket-Status Update
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

    COMMIT TRANSACTION;

    SELECT @@ROWCOUNT AS RowsAffected;
END
GO

-- =============================================
-- Basis-Daten einfügen
-- =============================================

-- Admin-User
INSERT INTO Employees (RFIDTag, Name, Department, Role, Language, Email)
VALUES ('ADMIN001', 'Administrator', 'IT', 'Administrator', 'de', 'admin@shirtful.de');

-- System-Einstellungen
INSERT INTO Settings (Category, Name, Value, DataType, Description)
VALUES
    ('System', 'Version', '1.0.0', 'string', 'System-Version'),
    ('System', 'DatabaseVersion', '001', 'string', 'Datenbank-Version'),
    ('System', 'InstallDate', CONVERT(VARCHAR, GETDATE(), 120), 'datetime', 'Installations-Datum');

-- Migration als angewendet markieren
INSERT INTO DatabaseMigrations (Version, Description)
VALUES ('001_initial_schema', 'Initiales Datenbankschema für Shirtful WMS');

PRINT 'Migration 001_initial_schema erfolgreich angewendet.';
GO