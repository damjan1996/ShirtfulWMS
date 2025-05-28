# Shirtful WMS - Datenbank Schema

## Übersicht

Das Shirtful WMS verwendet Microsoft SQL Server als Datenbank-Backend. Das Schema ist optimiert für die Verfolgung von Paketen durch verschiedene Produktionsstadien.

## Entity-Relationship Diagramm

```
Employees ----< TimeTracking
    |
    +--------< PackageHistory >---- Packages >---- Deliveries
    |                                  |
    +--------< QualityIssues >---------+
    |
    +--------< AuditLog
    |
    +--------< Settings
```

## Tabellen

### 1. Employees (Mitarbeiter)

Speichert alle Mitarbeiterdaten für Authentifizierung und Tracking.

```sql
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
```

**Indizes:**
- `IX_Employees_RFID` auf RFIDTag
- `IX_Employees_Active` auf IsActive

**Beispieldaten:**
```sql
INSERT INTO Employees (RFIDTag, Name, Department, Role, Language)
VALUES ('12345678', 'Max Mustermann', 'Lager', 'Lagerarbeiter', 'de');
```

### 2. Deliveries (Lieferungen)

Verwaltet eingehende Warenlieferungen.

```sql
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
```

**Status-Werte:**
- `Offen` - Lieferung läuft
- `Abgeschlossen` - Lieferung komplett
- `Abgebrochen` - Lieferung abgebrochen

### 3. Packages (Pakete)

Zentrale Tabelle für alle Pakete im System.

```sql
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
```

**CurrentStage-Werte:**
- `Wareneingang`
- `In Veredelung`
- `In Betuchung`
- `Qualitätskontrolle`
- `Qualität OK`
- `Nacharbeit erforderlich`
- `Versandbereit`
- `Versendet`
- `Storniert`

**Priority-Werte:**
- `Niedrig`
- `Normal`
- `Hoch`
- `Express`
- `Dringend`

### 4. PackageHistory (Paket-Historie)

Vollständige Historie aller Statusänderungen.

```sql
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
```

### 5. TimeTracking (Zeiterfassung)

Arbeitszeiten der Mitarbeiter.

```sql
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
```

**Berechnete Spalte:**
- `WorkMinutes` - Automatisch berechnete Arbeitsminuten

### 6. QualityIssues (Qualitätsprobleme)

Dokumentation von Qualitätsmängeln.

```sql
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
```

**IssueType-Werte:**
- `Druckfehler`
- `Farbabweichung`
- `Positionsfehler`
- `Stoffdefekt`
- `Verschmutzung`
- `Falsche Größe`
- `Nahtfehler`

### 7. Settings (Einstellungen)

System-Einstellungen als Key-Value Store.

```sql
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
```

### 8. AuditLog (Audit-Log)

Protokollierung aller Änderungen für Compliance.

```sql
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
```

### 9. DatabaseMigrations (Migrationen)

Tracking von Datenbank-Migrationen.

```sql
CREATE TABLE DatabaseMigrations (
    MigrationID INT IDENTITY(1,1) PRIMARY KEY,
    Version VARCHAR(50) NOT NULL UNIQUE,
    Description NVARCHAR(200),
    AppliedAt DATETIME DEFAULT GETDATE(),
    AppliedBy NVARCHAR(100) DEFAULT SYSTEM_USER
);
```

## Views

### vw_CurrentPackages

Übersicht aller aktiven Pakete (nicht versendete).

```sql
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
    DATEDIFF(HOUR, p.CreatedAt, GETDATE()) AS AgeHours
FROM Packages p
LEFT JOIN Employees e1 ON p.CreatedBy = e1.EmployeeID
LEFT JOIN Employees e2 ON p.LastUpdatedBy = e2.EmployeeID
LEFT JOIN Deliveries d ON p.DeliveryID = d.DeliveryID
WHERE p.CurrentStage != 'Versendet';
```

### vw_DailyStatistics

Tagesstatistiken nach Datum.

```sql
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
    SUM(CASE WHEN p.CurrentStage = 'Versendet' THEN 1 ELSE 0 END) AS Shipped
FROM Packages p
GROUP BY CAST(p.CreatedAt AS DATE);
```

### vw_EmployeePerformance

Mitarbeiter-Performance Übersicht.

```sql
CREATE VIEW vw_EmployeePerformance AS
SELECT 
    e.EmployeeID,
    e.Name,
    e.Department,
    e.Role,
    COUNT(DISTINCT ph.PackageID) AS PackagesProcessed,
    COUNT(DISTINCT CAST(ph.Timestamp AS DATE)) AS DaysWorked,
    AVG(ph.Duration) AS AvgProcessingMinutes,
    MAX(ph.Timestamp) AS LastActivity
FROM Employees e
LEFT JOIN PackageHistory ph ON e.EmployeeID = ph.EmployeeID
WHERE e.IsActive = 1
GROUP BY e.EmployeeID, e.Name, e.Department, e.Role;
```

## Stored Procedures

### sp_UpdatePackageStatus

Aktualisiert Paketstatus mit Historie.

```sql
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
        UPDATE Packages SET ProcessingStarted = GETDATE(), ProcessingBy = @EmployeeID 
        WHERE PackageID = @PackageID;
    
    COMMIT TRANSACTION;
    
    SELECT @@ROWCOUNT AS RowsAffected;
END
```

### sp_DailyCloseout

Tagesabschluss-Statistiken.

```sql
CREATE PROCEDURE sp_DailyCloseout
    @Date DATE = NULL
AS
BEGIN
    -- Statistiken für einen Tag
    -- Packages received, shipped, issues, active employees
    -- Top performers
    -- Problematic packages (>48h)
END
```

## Trigger

### tr_Packages_Audit

Audit-Trigger für Paket-Änderungen.

```sql
CREATE TRIGGER tr_Packages_Audit
ON Packages
AFTER UPDATE
AS
BEGIN
    -- Loggt alle Änderungen in AuditLog
    -- Besonders CurrentStage-Änderungen
END
```

## Indizes

Wichtige Indizes für Performance:

1. **Packages**
   - `IX_Packages_QR` - QRCode (Unique)
   - `IX_Packages_Order` - OrderID
   - `IX_Packages_Customer` - CustomerName
   - `IX_Packages_Stage` - CurrentStage
   - `IX_Packages_Created` - CreatedAt
   - `IX_Packages_Priority` - Priority

2. **PackageHistory**
   - `IX_History_Package` - PackageID
   - `IX_History_Time` - Timestamp
   - `IX_History_Employee` - EmployeeID

## Wartung

### Backup-Strategie

```sql
-- Tägliches Backup
BACKUP DATABASE ShirtfulWMS
TO DISK = 'C:\Backups\ShirtfulWMS_20240501.bak'
WITH COMPRESSION, INIT;
```

### Index-Wartung

```sql
-- Index-Rebuild (wöchentlich)
ALTER INDEX ALL ON Packages REBUILD;
ALTER INDEX ALL ON PackageHistory REBUILD;
```

### Statistiken aktualisieren

```sql
-- Statistiken aktualisieren (täglich)
UPDATE STATISTICS Packages WITH FULLSCAN;
UPDATE STATISTICS PackageHistory WITH FULLSCAN;
```

## Performance-Tipps

1. **Partitionierung**: Bei >1 Mio. Paketen PackageHistory nach Monat partitionieren
2. **Archivierung**: Alte Daten (>1 Jahr) in Archiv-Tabellen verschieben
3. **Indizes**: Regelmäßige Index-Wartung
4. **Statistiken**: Auto-Update-Statistics aktiviert
5. **Connection Pooling**: In Anwendung aktiviert

## Sicherheit

1. **Berechtigungen**: Anwendung nutzt eigenen DB-User
2. **Verschlüsselung**: TDE für sensible Daten empfohlen
3. **Audit**: Alle Änderungen werden geloggt
4. **Backup**: Tägliche Backups mit Verschlüsselung
5. **Zugriff**: Nur über Anwendung, kein direkter DB-Zugriff