-- =============================================
-- Shirtful WMS - Beispieldaten für Tests
-- Version: 1.0.0
-- WARNUNG: Nur für Test/Entwicklung verwenden!
-- =============================================

USE ShirtfulWMS;
GO

-- =============================================
-- Zusätzliche Mitarbeiter
-- =============================================
INSERT INTO Employees (RFIDTag, Name, Department, Role, Language, Email, Phone)
VALUES
    -- Lager
    ('11111111', 'Anna Schmidt', 'Lager', 'Lagerarbeiter', 'de', 'anna.schmidt@shirtful.de', '+49 30 1234561'),
    ('22222222', 'Tom Weber', 'Lager', 'Lagerarbeiter', 'de', 'tom.weber@shirtful.de', '+49 30 1234562'),
    ('33333333', 'Maria Garcia', 'Lager', 'Teamleiter', 'de', 'maria.garcia@shirtful.de', '+49 30 1234563'),

    -- Veredelung
    ('44444444', 'Klaus Meyer', 'Veredelung', 'Drucker', 'de', 'klaus.meyer@shirtful.de', '+49 30 1234564'),
    ('55555555', 'Lisa Müller', 'Veredelung', 'Drucker', 'de', 'lisa.mueller@shirtful.de', '+49 30 1234565'),
    ('66666666', 'Ahmed Yilmaz', 'Veredelung', 'Drucker', 'tr', 'ahmed.yilmaz@shirtful.de', '+49 30 1234566'),

    -- Betuchung
    ('77777777', 'Sophie Klein', 'Betuchung', 'Textilarbeiter', 'de', 'sophie.klein@shirtful.de', '+49 30 1234567'),
    ('88888888', 'Jan Kowalski', 'Betuchung', 'Textilarbeiter', 'pl', 'jan.kowalski@shirtful.de', '+49 30 1234568'),

    -- Qualitätskontrolle
    ('99999999', 'Emma Brown', 'Qualitätskontrolle', 'Prüfer', 'en', 'emma.brown@shirtful.de', '+49 30 1234569'),
    ('AAAAAAAA', 'Felix Wagner', 'Qualitätskontrolle', 'Prüfer', 'de', 'felix.wagner@shirtful.de', '+49 30 1234570'),

    -- Versand
    ('BBBBBBBB', 'Julia Hoffmann', 'Versand', 'Versandmitarbeiter', 'de', 'julia.hoffmann@shirtful.de', '+49 30 1234571'),
    ('CCCCCCCC', 'Michael Schulz', 'Versand', 'Versandmitarbeiter', 'de', 'michael.schulz@shirtful.de', '+49 30 1234572');

PRINT 'Zusätzliche Mitarbeiter eingefügt';
GO

-- =============================================
-- Test-Lieferungen
-- =============================================
DECLARE @DeliveryID1 INT, @DeliveryID2 INT, @DeliveryID3 INT;

INSERT INTO Deliveries (Supplier, DeliveryNote, ExpectedPackages, ReceivedPackages, ReceivedBy, Status)
VALUES ('DHL', 'LS-2024-001', 10, 10, 1, 'Abgeschlossen');
SET @DeliveryID1 = SCOPE_IDENTITY();

INSERT INTO Deliveries (Supplier, DeliveryNote, ExpectedPackages, ReceivedPackages, ReceivedBy, Status)
VALUES ('UPS', 'LS-2024-002', 15, 12, 2, 'Offen');
SET @DeliveryID2 = SCOPE_IDENTITY();

INSERT INTO Deliveries (Supplier, DeliveryNote, ExpectedPackages, ReceivedPackages, ReceivedBy, Status)
VALUES ('DPD', 'LS-2024-003', 8, 8, 3, 'Abgeschlossen');
SET @DeliveryID3 = SCOPE_IDENTITY();

PRINT 'Test-Lieferungen eingefügt';
GO

-- =============================================
-- Test-Pakete mit verschiedenen Status
-- =============================================

-- Pakete in verschiedenen Stadien
DECLARE @Counter INT = 1;
DECLARE @MaxPackages INT = 50;
DECLARE @Customers TABLE (Name NVARCHAR(100));
DECLARE @Products TABLE (Name NVARCHAR(100));

-- Beispiel-Kunden
INSERT INTO @Customers VALUES
    ('Sport Müller GmbH'),
    ('Fashion Store Berlin'),
    ('T-Shirt Paradise'),
    ('Textil König'),
    ('Mode Express'),
    ('Shirt & Co'),
    ('Druckerei Schmidt'),
    ('Werbe-Textilien AG'),
    ('Event Shirts GmbH'),
    ('Corporate Fashion');

-- Beispiel-Produkte
INSERT INTO @Products VALUES
    ('T-Shirt Basic'),
    ('Polo-Shirt Premium'),
    ('Hoodie Comfort'),
    ('Sweatshirt Classic'),
    ('Tank Top Sport'),
    ('Langarmshirt'),
    ('V-Neck Shirt'),
    ('Rundhals Shirt'),
    ('Damen T-Shirt'),
    ('Herren Polo');

-- Pakete generieren
WHILE @Counter <= @MaxPackages
BEGIN
    DECLARE @QRCode VARCHAR(50) = 'PKG-2024-' + RIGHT('000000' + CAST(@Counter AS VARCHAR), 6);
    DECLARE @OrderID VARCHAR(50) = 'ORD-2024-' + RIGHT('0000' + CAST(@Counter AS VARCHAR), 4);
    DECLARE @Customer NVARCHAR(100) = (SELECT TOP 1 Name FROM @Customers ORDER BY NEWID());
    DECLARE @ItemCount INT = FLOOR(RAND() * 20) + 1;
    DECLARE @Priority NVARCHAR(20) = CASE
        WHEN @Counter % 10 = 0 THEN 'Express'
        WHEN @Counter % 5 = 0 THEN 'Hoch'
        ELSE 'Normal'
    END;
    DECLARE @Stage NVARCHAR(50) = CASE
        WHEN @Counter <= 5 THEN 'Wareneingang'
        WHEN @Counter <= 10 THEN 'In Veredelung'
        WHEN @Counter <= 15 THEN 'In Betuchung'
        WHEN @Counter <= 20 THEN 'Qualitätskontrolle'
        WHEN @Counter <= 25 THEN 'Qualität OK'
        WHEN @Counter <= 30 THEN 'Versandbereit'
        WHEN @Counter <= 35 THEN 'Versendet'
        WHEN @Counter <= 40 THEN 'Nacharbeit erforderlich'
        ELSE 'Wareneingang'
    END;

    INSERT INTO Packages (
        QRCode, OrderID, CustomerName, ItemCount, Priority, CurrentStage,
        DeliveryID, CreatedBy, CreatedAt, LastUpdate, LastUpdatedBy
    )
    VALUES (
        @QRCode, @OrderID, @Customer, @ItemCount, @Priority, @Stage,
        CASE WHEN @Counter % 3 = 0 THEN 1 WHEN @Counter % 3 = 1 THEN 2 ELSE 3 END,
        (@Counter % 5) + 1,
        DATEADD(DAY, -(@MaxPackages - @Counter), GETDATE()),
        DATEADD(HOUR, -(@MaxPackages - @Counter), GETDATE()),
        (@Counter % 5) + 1
    );

    -- Historie für jedes Paket
    DECLARE @PackageID INT = SCOPE_IDENTITY();

    -- Wareneingang
    INSERT INTO PackageHistory (PackageID, Stage, EmployeeID, Timestamp, Duration)
    VALUES (@PackageID, 'Wareneingang', 1, DATEADD(DAY, -(@MaxPackages - @Counter), GETDATE()), 15);

    -- Weitere Stages je nach aktuellem Status
    IF @Stage IN ('In Veredelung', 'In Betuchung', 'Qualitätskontrolle', 'Qualität OK', 'Versandbereit', 'Versendet', 'Nacharbeit erforderlich')
    BEGIN
        INSERT INTO PackageHistory (PackageID, Stage, EmployeeID, Timestamp, Duration)
        VALUES (@PackageID, 'In Veredelung', 4, DATEADD(HOUR, -(@MaxPackages - @Counter - 6), GETDATE()), 45);
    END

    IF @Stage IN ('In Betuchung', 'Qualitätskontrolle', 'Qualität OK', 'Versandbereit', 'Versendet', 'Nacharbeit erforderlich')
    BEGIN
        INSERT INTO PackageHistory (PackageID, Stage, EmployeeID, Timestamp, Duration)
        VALUES (@PackageID, 'In Betuchung', 7, DATEADD(HOUR, -(@MaxPackages - @Counter - 4), GETDATE()), 30);
    END

    IF @Stage IN ('Qualitätskontrolle', 'Qualität OK', 'Versandbereit', 'Versendet', 'Nacharbeit erforderlich')
    BEGIN
        INSERT INTO PackageHistory (PackageID, Stage, EmployeeID, Timestamp, Duration)
        VALUES (@PackageID, 'Qualitätskontrolle', 9, DATEADD(HOUR, -(@MaxPackages - @Counter - 2), GETDATE()), 10);
    END

    -- Qualitätsprobleme für einige Pakete
    IF @Stage = 'Nacharbeit erforderlich'
    BEGIN
        INSERT INTO QualityIssues (PackageID, IssueType, Description, ReportedBy, ReportedAt)
        VALUES (
            @PackageID,
            CASE @Counter % 3
                WHEN 0 THEN 'Druckfehler'
                WHEN 1 THEN 'Farbabweichung'
                ELSE 'Positionsfehler'
            END,
            'Qualitätsmangel festgestellt - Nacharbeit erforderlich',
            9,
            DATEADD(HOUR, -(@MaxPackages - @Counter - 2), GETDATE())
        );

        UPDATE Packages
        SET QualityStatus = 'Nacharbeit',
            QualityCheckedBy = 9,
            QualityCheckDate = DATEADD(HOUR, -(@MaxPackages - @Counter - 2), GETDATE())
        WHERE PackageID = @PackageID;
    END

    -- Versandinformationen für versendete Pakete
    IF @Stage = 'Versendet'
    BEGIN
        UPDATE Packages
        SET ShippingMethod = CASE @Counter % 4
                WHEN 0 THEN 'DHL Express'
                WHEN 1 THEN 'UPS'
                WHEN 2 THEN 'DPD'
                ELSE 'GLS'
            END,
            TrackingNumber = 'TRACK-' + CAST(@PackageID AS VARCHAR) + '-2024',
            ShippedBy = 11,
            ShippedAt = DATEADD(HOUR, -(@MaxPackages - @Counter), GETDATE())
        WHERE PackageID = @PackageID;
    END

    SET @Counter = @Counter + 1;
END

PRINT '50 Test-Pakete mit Historie eingefügt';
GO

-- =============================================
-- Zeiterfassungs-Einträge
-- =============================================

-- Heute
INSERT INTO TimeTracking (EmployeeID, ClockIn, ClockOut, BreakMinutes, Station)
VALUES
    (1, DATEADD(HOUR, -8, GETDATE()), NULL, 0, 'Wareneingang'),
    (4, DATEADD(HOUR, -7, GETDATE()), NULL, 30, 'Veredelung'),
    (7, DATEADD(HOUR, -6, GETDATE()), NULL, 0, 'Betuchung'),
    (9, DATEADD(HOUR, -5, GETDATE()), NULL, 0, 'Qualitätskontrolle'),
    (11, DATEADD(HOUR, -4, GETDATE()), NULL, 0, 'Warenausgang');

-- Gestern (abgeschlossene Schichten)
INSERT INTO TimeTracking (EmployeeID, ClockIn, ClockOut, BreakMinutes, Station)
VALUES
    (1, DATEADD(DAY, -1, DATEADD(HOUR, -16, GETDATE())), DATEADD(DAY, -1, DATEADD(HOUR, -8, GETDATE())), 30, 'Wareneingang'),
    (2, DATEADD(DAY, -1, DATEADD(HOUR, -16, GETDATE())), DATEADD(DAY, -1, DATEADD(HOUR, -8, GETDATE())), 30, 'Wareneingang'),
    (4, DATEADD(DAY, -1, DATEADD(HOUR, -15, GETDATE())), DATEADD(DAY, -1, DATEADD(HOUR, -7, GETDATE())), 30, 'Veredelung'),
    (5, DATEADD(DAY, -1, DATEADD(HOUR, -14, GETDATE())), DATEADD(DAY, -1, DATEADD(HOUR, -6, GETDATE())), 30, 'Veredelung');

PRINT 'Zeiterfassungs-Einträge eingefügt';
GO

-- =============================================
-- Zusätzliche Einstellungen
-- =============================================

INSERT INTO Settings (Category, Name, Value, DataType, Description)
VALUES
    ('Printer', 'LabelPrinter', 'Zebra ZD420', 'string', 'Label-Drucker Modell'),
    ('Printer', 'LabelPrinterPort', 'USB001', 'string', 'Drucker-Port'),
    ('Printer', 'LabelSize', '100x50mm', 'string', 'Label-Größe'),
    ('Scanner', 'BeepVolume', '50', 'int', 'Lautstärke des Scan-Tons (0-100)'),
    ('Scanner', 'AutoFocusDelay', '500', 'int', 'Autofokus-Verzögerung in ms'),
    ('UI', 'ColorScheme', 'blue', 'string', 'Farbschema der Oberfläche'),
    ('UI', 'FontScale', '1.0', 'float', 'Schrift-Skalierung'),
    ('Alerts', 'PackageAgeWarning', '24', 'int', 'Warnung bei Paketen älter als X Stunden'),
    ('Alerts', 'PackageAgeCritical', '48', 'int', 'Kritisch bei Paketen älter als X Stunden');

PRINT 'Zusätzliche Einstellungen eingefügt';
GO

-- =============================================
-- Zusammenfassung
-- =============================================

PRINT '';
PRINT '=============================================';
PRINT 'Beispieldaten erfolgreich eingefügt';
PRINT '=============================================';
PRINT '';

-- Statistiken anzeigen
SELECT 'Mitarbeiter' AS Tabelle, COUNT(*) AS Anzahl FROM Employees
UNION ALL
SELECT 'Lieferungen', COUNT(*) FROM Deliveries
UNION ALL
SELECT 'Pakete', COUNT(*) FROM Packages
UNION ALL
SELECT 'Paket-Historie', COUNT(*) FROM PackageHistory
UNION ALL
SELECT 'Qualitätsprobleme', COUNT(*) FROM QualityIssues
UNION ALL
SELECT 'Zeiterfassung', COUNT(*) FROM TimeTracking
UNION ALL
SELECT 'Einstellungen', COUNT(*) FROM Settings;

-- Status-Übersicht
PRINT '';
PRINT 'Paket-Status Übersicht:';
SELECT CurrentStage AS Status, COUNT(*) AS Anzahl
FROM Packages
GROUP BY CurrentStage
ORDER BY COUNT(*) DESC;

PRINT '';
PRINT 'Test-Daten bereit für Entwicklung und Tests!';
GO