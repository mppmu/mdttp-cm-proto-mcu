# QSSI Interface Manual
## cm_mcu_hwtest Firmware — MDT-TP CM Prototype MCU

---

## 1. Overview

The QSSI (Quad Synchronous Serial Interface) provides access to the external
SPI/QSPI flash memory device. It is implemented on top of the TM4C1294 SSI1
peripheral using TivaWare's advanced SSI mode, which supports both standard SPI
(single-bit data) and Quad SPI (four-bit data) with hardware CS (FSS) control.

**Connected device:** IS25LP064A-JBLA3 — ISSI 64 Mbit SPI/QSPI NOR Flash

---

## 2. Hardware Configuration

| Signal | MCU Pin | GPIO      |
|--------|---------|-----------|
| CLK    | PB5     | SSI1CLK   |
| FSS/CS | PB4     | SSI1FSS   |
| XDAT0  | PE4     | SSI1XDAT0 |
| XDAT1  | PE5     | SSI1XDAT1 |
| XDAT2  | PD4     | SSI1XDAT2 |
| XDAT3  | PD5     | SSI1XDAT3 |

- **Protocol:** Motorola SPI Mode 0 (CPOL=0, CPHA=0)
- **Data width:** 8 bits
- **Default bit rate:** 15 MHz
- **Supported bit rate:** 2 kHz – 50 MHz
- **Timeout:** 500 loop iterations (~10 µs each)

---

## 3. Commands

### 3.1 `qssi-s` — Set Up the QSSI Port

```
qssi-s PORT FREQ
```

| Parameter | Description |
|-----------|-------------|
| `PORT`    | QSSI port number. Only `1` is supported. |
| `FREQ`    | Bit rate in Hz. Valid range: 2000 – 50000000. |

**Example — set to 1 MHz:**
```
qssi-s 1 1000000
```

Must be called after power-on before any `qssi` access. The default bit rate
at startup is 15 MHz.

---

### 3.2 `qssi` — QSSI Access (Read / Write)

```
qssi PORT MODE RW END DATA...
```

| Parameter | Description        | Values                                          |
|-----------|--------------------|-------------------------------------------------|
| `PORT`    | QSSI port number   | `1`                                             |
| `MODE`    | SPI data mode      | `0` = standard SPI (1-bit), `1` = Quad SPI (4-bit) |
| `RW`      | Transfer direction | `0` = write, `1` = read                         |
| `END`     | Release CS after   | `0` = hold CS, `1` = release CS                 |
| `DATA...` | Write: bytes to send (up to 28). Read: number of bytes to receive. | |

Numbers can be given in decimal or hex (`0x` prefix).

---

## 4. CS (Chip Select) Control

The `END` flag controls the hardware FSS line:

- `END=1`: CS is released after the last byte. Use for self-contained
  single-phase transactions (e.g. Write Enable, Bulk Erase).
- `END=0`: CS is held low after the transfer. Use when the next `qssi` call
  must belong to the same transaction (e.g. sending a read command before
  clocking out data).

> **Important:** When `END=0`, the driver does not wait for the SSI to become
> idle before returning. Issue the next command only after a short pause to
> avoid a timeout error on the following read.

---

## 5. IS25LP064A Flash Command Reference

### 5.1 Identification

**Read JEDEC ID** — verify the device is responding:
```
qssi 1 0 0 0 0x9F
qssi 1 0 1 1 3
```
Expected: `0x9D 0x60 0x17`
(Manufacturer: ISSI, Type: SPI Flash, Capacity: 64 Mbit)

---

### 5.2 Status Register

**Read Status Register** (opcode `0x05`):
```
qssi 1 0 0 0 0x05
qssi 1 0 1 1 1
```

| Bit | Name | Description                                      |
|-----|------|--------------------------------------------------|
| 0   | WIP  | Write In Progress. `1` = busy (erase/write ongoing). |
| 1   | WEL  | Write Enable Latch. `1` = write enable active.   |

Poll until WIP = 0 after any erase or write operation before issuing the next
command.

---

### 5.3 Write Enable

Must be issued before every erase and every page program. The WEL bit is
automatically cleared by the flash after the operation completes.

```
qssi 1 0 0 1 0x06
```

---

### 5.4 Erase Operations

Flash bits can only transition from `1` to `0` during a write. To restore bits
to `1`, a sector or bulk erase is required first.

**Sector Erase (4 KB)** — opcode `0x20`, 3-byte address:
```
qssi 1 0 0 1 0x06
qssi 1 0 0 1 0x20 0xAA 0xBB 0xCC
```
Poll WIP until clear (~80 ms typical).

**Bulk Erase (full chip)** — opcode `0x60`:
```
qssi 1 0 0 1 0x06
qssi 1 0 0 1 0x60
```
Poll WIP until clear (~30 s typical).

---

### 5.5 Read Operations

**Standard Read** (opcode `0x03`, up to 33 MHz):
```
qssi 1 0 0 0 0x03 0xAA 0xBB 0xCC
qssi 1 0 1 1 N
```

**Fast Read** (opcode `0x0B`, up to 108 MHz, requires 1 dummy byte after address):
```
qssi 1 0 0 0 0x0B 0xAA 0xBB 0xCC 0x00
qssi 1 0 1 1 N
```

**Quad Output Fast Read** (opcode `0x6B`, data phase in quad mode):
```
qssi 1 0 0 0 0x6B 0xAA 0xBB 0xCC 0x00
qssi 1 1 1 1 N
```

---

### 5.6 Write Operations (Page Program)

A page is 256 bytes. Writes cannot cross a page boundary — if address + length
exceeds the boundary, the write wraps within the same page. The target sector
must be erased before writing.

**Standard Page Program** (opcode `0x02`):
```
qssi 1 0 0 1 0x06
qssi 1 0 0 1 0x02 0xAA 0xBB 0xCC 0xD1 0xD2 0xD3
```
Poll WIP until clear (~0.8 ms typical).

**Quad Page Program** (opcode `0x32`, data phase in quad mode):
```
qssi 1 0 0 1 0x06
qssi 1 0 0 0 0x32 0xAA 0xBB 0xCC
qssi 1 1 0 1 0xD1 0xD2 0xD3 0xD4
```
Poll WIP until clear.

---

## 6. Typical Session

```
# 1. Set bit rate to 10 MHz
qssi-s 1 10000000

# 2. Check device ID
qssi 1 0 0 0 0x9F
qssi 1 0 1 1 3
# Expected: OK. Data: 0x9d 0x60 0x17

# 3. Erase sector at address 0x000000
qssi 1 0 0 1 0x06
qssi 1 0 0 1 0x20 0x00 0x00 0x00
# Poll WIP until 0:
qssi 1 0 0 0 0x05
qssi 1 0 1 1 1

# 4. Write 4 bytes to address 0x000000
qssi 1 0 0 1 0x06
qssi 1 0 0 1 0x02 0x00 0x00 0x00 0xDE 0xAD 0xBE 0xEF
# Poll WIP until 0:
qssi 1 0 0 0 0x05
qssi 1 0 1 1 1

# 5. Read back 4 bytes from address 0x000000
qssi 1 0 0 0 0x03 0x00 0x00 0x00
qssi 1 0 1 1 4
# Expected: OK. Data: 0xde 0xad 0xbe 0xef
```

---

## 7. Source Files

| File | Description |
|------|-------------|
| `Firmware/Common/hw/qssi/qssi.c` | Low-level SSI driver (init, read, write) |
| `Firmware/Common/hw/qssi/qssi.h` | `tQSSI` struct definition and prototypes |
| `Firmware/Projects/cm_mcu_hwtest/cm_mcu_hwtest_qssi.c` | Command parser for `qssi` and `qssi-s` |
| `Firmware/Projects/cm_mcu_hwtest/cm_mcu_hwtest_io.c` | Hardware configuration (`g_sQssi1` struct) |
| `Firmware/Projects/cm_mcu_hwtest/cm_mcu_hwtest.h` | Frequency limit constants (`QSSI_FREQ_MIN/MAX`) |
