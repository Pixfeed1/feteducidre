-- Add status column to invoices table
ALTER TABLE invoices
    ADD COLUMN `status` ENUM('paid', 'pending', 'overdue', 'refunded') NOT NULL DEFAULT 'pending' AFTER `total`;
