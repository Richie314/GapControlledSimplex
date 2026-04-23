"""
netlib_emps.py - Expand compressed LP programs (netlib format) to MPS format.

Python port of emps.c by David M. Gay (AT&T Bell Laboratories).

See the original c version at https://www.netlib.org/lp/data/emps.c

The netlib LP archive stores problems in a compressed ASCII encoding.
This module decodes that format and writes standard MPS output.

Public API
----------
expand_mps(input_file, output_file=None, *, keepmyst, blanksubst, just1)
    Convert one compressed LP file.  Returns MPS text when output_file
    is None; otherwise writes to output_file and returns None.

expand_mps_string(text, ...)
    Accepts the compressed text as a str; returns MPS text as a str.

Command line usage
------------------
This file can be used as a command-line tool as well. The options mirror the original C program.
See also `gsimplex-emps --help` for usage information.
"""

from __future__ import annotations

import io
import sys
import argparse
from typing import List, Optional, Tuple, TextIO

# ---------------------------------------------------------------------------
# Translation table  (identical to the C original)
# ---------------------------------------------------------------------------
TRTAB: str = (
    "!\"#$%&'()*+,-./0123456789;<=>?@"
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ[]^_`"
    "abcdefghijklmnopqrstuvwxyz{|}~"
)

_INVTRTAB: List[int] = [92] * 256
for _i, _ch in enumerate(TRTAB):
    _INVTRTAB[ord(_ch)] = _i


def _tr(c: str) -> int:
    """Return the inverse-translation-table value for a character."""

    return _INVTRTAB[ord(c) & 0xFF]


# ---------------------------------------------------------------------------
# Low-level decoders  (stateless)
# ---------------------------------------------------------------------------

def _exindx(z: str, zi: int) -> Tuple[int, int]:
    """Decode one variable-length supersparse index.

    Mirrors exindx() in the C source.  Characters with tr-value 23-45
    encode a single-character terminal (value = k-23).  Characters with
    tr-value 0-22 start a multi-character base-46 sequence that ends when
    a character with tr-value >= 46 is encountered (the terminal 'bit').

    Parameters
    ----------
    z   : current data string (one stripped line from the compressed file)
    zi  : current read offset within *z*

    Returns
    -------
    (index_value, new_zi)
    """

    k = _tr(z[zi]); zi += 1
    if k >= 46:
        raise ValueError(f"exindx: bad encoded byte at offset {zi - 1}")
    if k >= 23:
        return k - 23, zi
    
    # Multi-character base-46 variable-length encoding
    x = k
    while True:
        k = _tr(z[zi]); zi += 1
        x = x * 46 + k
        if k >= 46:
            x -= 46
            break
    
    return x, zi


def _exform(
    z: str, zi: int, ss: List[str], kmax: int
) -> Tuple[str, int]:
    """Decode one compressed floating-point number.

    Mirrors exform() in the C source.

    When the first encoded character has tr-value < 46 the number is a
    supersparse reference into the pre-computed table *ss*.  Otherwise the
    number is encoded inline as either integer-float (k >= 11 after sign
    adjustment) or general float.

    Parameters
    ----------
    z     : current data string
    zi    : current read offset within *z*
    ss    : pre-computed number table, **1-based** (ss[0] unused)
    kmax  : number of valid entries in *ss* (== len(ss) - 1)

    Returns
    -------
    (formatted_string, new_zi)
    The string is right-justified in a field of at least 12 characters,
    matching the C padding logic ``while(k++ < 12) *s++ = ' '``.
    """
    y: int = 0
    k: int = _tr(z[zi]); zi += 1

    # Supersparse table reference 
    if k < 46:
        # The index encoding starts at the character we already read;
        # back up one so _exindx can re-consume the full encoding.
        idx, zi = _exindx(z, zi - 1)
        if idx > kmax:
            raise ValueError(
                f"exform: table reference {idx} exceeds kmax {kmax}"
            )
        return ss[idx], zi

    # Inline encoded number 
    k -= 46
    neg = k >= 23
    if neg:
        k -= 23
        nelim = 11
    else:
        nelim = 12

    # d[] holds decimal digit characters, least-significant first
    # (mirrors the db[] buffer + d pointer pattern in the C source).
    d: List[str] = []

    if k >= 11:
        # Integer floating-point 
        # '.' is stored first so that reversing d places it after the
        # digits, yielding output like "123." (integer with trailing point).
        k -= 11
        d.append('.')
        if k >= 6:
            x: int = k - 6
        else:
            x = k
            while True:
                k = _tr(z[zi]); zi += 1
                x = x * 46 + k
                if k >= 46:
                    x -= 46
                    break
        if x == 0:
            d.append('0')
        else:
            while x:
                d.append(str(x % 10))
                x //= 10
        sbuf = list(reversed(d))          # MSB-first digits then '.'

    else:
        # General floating-point 
        ex: int = _tr(z[zi]) - 50;  zi += 1   # decimal exponent
        x        = _tr(z[zi]);      zi += 1   # start of base-92 mantissa
        kk       = k
        while kk > 0:
            kk -= 1
            if x >= 100_000_000:
                # High-part overflow: save x, restart x from new character
                y = x
                x = _tr(z[zi]); zi += 1
            else:
                x = x * 92 + _tr(z[zi]); zi += 1

        # Collect decimal digits of the mantissa (LSB first)
        if y:
            # y holds the high part; x holds the low extension.
            # C loop: while(x > 1) drain x digits, then drain y digits.
            while x > 1:
                d.append(str(x % 10))
                x //= 10
            yy = y
            while True:
                d.append(str(yy % 10))
                if yy < 10:
                    break
                yy //= 10
        elif x:
            xx = x
            while True:
                d.append(str(xx % 10))
                if xx < 10:
                    break
                xx //= 10
        else:
            d.append('0')

        # nd = number of digits that belong before the decimal point
        nd    = len(d) + ex
        sbuf  = []
        eout  = False

        if ex > 0:
            if nd < nelim or ex < 3:
                # All mantissa digits, trailing zeros, then '.'
                sbuf.extend(reversed(d))
                sbuf.extend(['0'] * ex)
                sbuf.append('.')
            else:
                eout = True
        elif nd >= 0:
            rev = list(reversed(d))
            sbuf.extend(rev[:nd])
            sbuf.append('.')
            sbuf.extend(rev[nd:])
        elif ex > -nelim:
            sbuf.append('.')
            sbuf.extend(['0'] * (-nd))
            sbuf.extend(reversed(d))
        else:
            eout = True

        if eout:
            # Scientific notation  (mirrors the Eout: label in the C source)
            ex += len(d) - 1
            rev   = list(reversed(d))
            ridx  = 0
            if ex == -10:
                # Special case: avoid a 3-digit exponent; accept slight
                # rounding error (mirrors the C original).
                ex = -9
                # No digits before '.'; fall through to the '.' append below
            else:
                # Optionally emit leading digits to reduce the exponent
                if ex > 9 and ex <= len(d) + 8:
                    while ex > 9:
                        sbuf.append(rev[ridx]); ridx += 1
                        ex -= 1
                sbuf.append(rev[ridx]); ridx += 1
            sbuf.append('.')
            sbuf.extend(rev[ridx:])
            sbuf.append('E')
            if ex < 0:
                sbuf.append('-')
                ex = -ex
            ed: List[str] = []
            while ex:
                ed.append(str(ex % 10))
                ex //= 10
            sbuf.extend(reversed(ed))

    result = ('-' if neg else '') + ''.join(sbuf)
    # Right-justify in a field of at least 12 characters
    # (matches C: while(k++ < 12) *s++ = ' ';  strcpy(s, sbuf);)
    return result.rjust(12), zi


# ---------------------------------------------------------------------------
# Converter class
# ---------------------------------------------------------------------------

class EMPSConverter:
    """Expand one or more compressed netlib LP problems to MPS format."""

    _BOUND_TYPES = ("UP", "LO", "FX", "FR", "MI", "PL")

    def __init__(
        self,
        *,
        keepmyst:   bool          = True,
        blanksubst: Optional[str] = None,
        just1:      bool          = False,
    ) -> None:
        """
        Parameters
        ----------
        keepmyst
            When True (default), "mystery lines" (lines starting with ':'
            in the source) are included in the output.
        blanksubst
            If given (e.g. '_'), blanks within names are replaced with
            this character.
        just1
            If True, emit only one nonzero per output line.
        """

        self.keepmyst   = keepmyst
        self.blanksubst = blanksubst
        self.just1      = just1

    # Public interface 

    def convert(
        self,
        input_file:  "str | TextIO",
        output_file: "str | TextIO | None" = None,
    ) -> Optional[str]:
        """Expand *input_file* and write the MPS result to *output_file*.

        Parameters
        ----------
        input_file
            A filesystem path or an already-opened readable text file.
        output_file
            A filesystem path, a writable text file, or None.
            When None the MPS text is returned as a string.

        Returns
        -------
        MPS text (str) when output_file is None; otherwise None.
        """

        return_str = output_file is None

        if isinstance(input_file, str):
            with open(input_file) as fh:
                result = self._run(fh, input_file)
        else:
            name   = getattr(input_file, 'name', '<stream>')
            result = self._run(input_file, name)

        if return_str:
            return result
        if isinstance(output_file, str):
            with open(output_file, 'w') as fh:
                fh.write(result)
        else:
            output_file.write(result)
        return None

    # Internal driver 

    def _run(self, inf: TextIO, infile_name: str) -> str:
        """Core loop; returns the complete MPS text as a single string."""
        # Per-run state 
        self._inf       = inf
        self._infile    = infile_name
        self._nline     = 0
        self._ncs       = 1        # next slot in the rolling checksum buffer
        self._canend    = False    # True -> EOF is acceptable
        self._kmax      = -1       # entries currently in the number table
        self._cn        = 0        # column name counter
        self._nrow      = 0
        self._ss: List[str] = []   # pre-computed number table (1-based)
        self._bs: List[str] = []   # name store (1-based via index-1)
        self._bsz       = 0        # capacity of _bs
        self._lastl     = ''
        # Checksum buffer: _chkbuf[0]=' ', checksum chars go into [1..71],
        # a '\n' is appended when reading the checksum verification line.
        self._chkbuf: List[str] = [' '] + ['\x00'] * 75
        self._cfn: List[str]    = [''] * 72   # filename per checksum slot
        self._cfl: List[int]    = [0]  * 72   # line no. per checksum slot
        self._out: List[str]    = []

        buf = self._rdline()
        while True:
            self._kmax = -1
            self._ncs  = 1

            # Skip lines until we find "NAME" 
            while buf is not None and not buf.startswith('NAME'):
                buf = self._rdline()
            if buf is None:
                break

            self._canend = False
            self._emit(buf)
            self._ncs = 1

            # Problem statistics: two encoded lines 
            s1 = (self._rdline() or '').split()
            s2 = (self._rdline() or '').split()
            try:
                nrow  = int(s1[0]);  ncol  = int(s1[1])
                # s1[2] = colmx  (unused)
                nz    = int(s1[3])
                # s1[4] = nrhs   (unused)
                rhsnz = int(s1[5])
                # s1[6] = nran   (unused)
                ranz  = int(s1[7])
                # s2[0] = nbd    (unused)
                bdnz  = int(s2[1])
                ns    = int(s2[2])
            except (IndexError, ValueError) as exc:
                raise RuntimeError(
                    f"Bad statistics lines in {self._infile}"
                ) from exc

            self._nrow  = nrow
            self._ncs   = 1
            self._cn    = nrow              # columns will be stored after rows
            self._bsz   = nrow + ncol
            self._bs    = ['        '] * self._bsz

            # Number table: ns pre-formatted floating-point strings 
            # Indexed 1-based; ss[0] is a placeholder that is never read.
            self._ss = [''] * (ns + 1)
            z, zi = '', 0
            for i in range(1, ns + 1):
                if zi >= len(z):
                    b = self._rdline()
                    z  = b if b is not None else ''
                    zi = 0
                val, zi       = _exform(z, zi, self._ss, self._kmax)
                self._ss[i]   = val
            self._kmax = ns

            # ROWS section 
            for i in range(1, nrow + 1):
                buf = self._rdline() or ''
                if i == 1:
                    self._emit('ROWS')
                row_type = buf[0] if buf else '?'
                row_name = buf[1:] if len(buf) > 1 else ''
                if self.blanksubst:
                    row_name = row_name.replace(' ', self.blanksubst)
                self._emit(f' {row_type}  {row_name}')
                self._namstore(i, row_name)

            # Data sections
            self._colout('COLUMNS', nz,    1)
            self._colout('RHS',     rhsnz, 2)
            self._colout('RANGES',  ranz,  3)
            self._colout('BOUNDS',  bdnz,  4)

            if self._ncs > 1:
                self._checkline()

            self._emit('ENDATA')

            # Look for another LP in the same file
            self._canend = True
            self._ncs    = 1
            buf = self._rdline()
            if buf is None:
                break

        return ''.join(self._out)

    def _emit(self, s: str) -> None:
        self._out.append(s if s.endswith('\n') else s + '\n')

    def _checkchar(self, s: str) -> None:
        """Update the rolling checksum with all characters of line *s*.

        Mirrors checkchar() in the C source.  The hash accumulates one
        character at a time; the final hash character (mod 92) is stored
        in _chkbuf[_ncs].
        """

        x = 0
        for c in s:
            if c == '\n':
                break
            cv = _tr(c)
            if x & 1:
                x = (x >> 1) + cv + 16384
            else:
                x = (x >> 1) + cv
        self._cfn[self._ncs] = self._infile
        self._cfl[self._ncs] = self._nline
        self._chkbuf[self._ncs] = TRTAB[x % 92]
        self._ncs += 1

    def _checkline(self) -> None:
        """Read and verify the next checksum line from the input.

        Mirrors checkline() in the C source.  The expected checksum line
        is _chkbuf[0.._ncs] = ' ' + (ncs-1 hash chars) + '\\n'.
        """

        self._canend = False
        while True:
            self._chkbuf[self._ncs] = '\n'
            expected = ''.join(self._chkbuf[:self._ncs + 1])
            self._nline += 1
            raw = self._inf.readline()
            if not raw:
                self._early_eof()
            if raw != expected:
                if raw.startswith(':') and self._ncs <= 72:

                    # Mystery line embedded at a checksum position
                    self._ncs -= 1
                    self._checkchar(raw)
                    if self.keepmyst:
                        self._emit(raw[1:].rstrip('\n'))
                    continue
                self._badchk(raw)
            break
        self._ncs = 1

    def _early_eof(self) -> None:
        self._lastl = ''
        raise RuntimeError(
            f"Premature end of file at line {self._nline} of {self._infile}"
        )

    def _badchk(self, got: str) -> None:
        expected = ''.join(self._chkbuf[:self._ncs + 1])
        # Identify the first mismatching slot to report the corrupt data line
        for i in range(1, self._ncs + 1):
            if i >= len(got) or got[i] != expected[i]:
                raise RuntimeError(
                    f"Checksum error: data line {self._cfl[i]} of "
                    f"{self._cfn[i]} appears corrupt\n"
                    f"  expected checksum line: {expected!r}\n"
                    f"  got:                    {got!r}"
                )
        raise RuntimeError(
            f"Checksum error:\n  expected: {expected!r}\n  got: {got!r}"
        )

    def _rdline(self) -> Optional[str]:
        """Read one data line; return None at EOF when _canend is True."""

        self._nline += 1
        raw = self._inf.readline()
        if not raw:
            if self._canend:
                return None
            self._early_eof()

        # Strip newline for processing (checkchar handles chars up to '\n')
        s = raw.rstrip('\n')
        self._checkchar(s)
        if self._ncs >= 72:
            self._checkline()

        # Mystery line: starts with ':'
        if s.startswith(':'):
            if self.keepmyst:
                self._emit(s[1:])
            return self._rdline()
        
        self._lastl = s
        return s

    def _namstore(self, i: int, s: str) -> None:
        """Store up to 8 characters of *s* at position *i* (1-based)."""

        if not (1 <= i <= self._bsz):
            raise RuntimeError(
                f"namstore: index {i} out of range [1, {self._bsz}]"
            )
        self._bs[i - 1] = (s + '        ')[:8]

    def _namfetch(self, i: int) -> str:
        """Retrieve the 8-character name stored at position *i* (1-based)."""

        if not (1 <= i <= self._bsz):
            raise RuntimeError(
                f"namfetch: index {i} out of range [1, {self._bsz}]"
            )
        return self._bs[i - 1]

    # Section output (COLUMNS / RHS / RANGES / BOUNDS) 

    def _colout(self, head: str, nz: int, what: int) -> None:
        """Output one MPS data section.

        Parameters
        ----------
        head : section header keyword
        nz   : number of nonzero/bound entries to process
        what : 1=COLUMNS, 2=RHS, 3=RANGES, 4=BOUNDS
        """

        BT = self._BOUND_TYPES

        if not nz:
            # Empty section: COLUMNS and RHS still print the header line
            if what <= 2:
                self._emit(head)
            return

        first        = True
        k            = 0           # pending nonzero counter (0 or 1)
        z, zi        = '', 0       # current data line and read position
        curcol       = ''
        rc1 = rc2    = ''
        rownm        = ['', '']

        while nz > 0:
            nz -= 1

            # Refill the line buffer when exhausted
            if zi >= len(z):
                b = self._rdline()
                z  = b if b is not None else ''
                zi = 0

            if first:
                self._emit(head)
                first = False

            # Consume new-column markers (index == 0) 
            # A zero index signals that a column name follows inline in z.
            n, zi = _exindx(z, zi)
            while n == 0:
                # Flush any pending single-nonzero output
                if k:
                    self._emit(
                        f'    {curcol:<8.8}  {rownm[0]:<8.8}  {rc1:.15}'
                    )
                    k = 0
                # The column name is the remaining data in z after the index
                seg = z[zi:] if zi < len(z) else head
                if self.blanksubst:
                    seg = seg.replace(' ', self.blanksubst)
                curcol = (seg + '        ')[:8]
                if what == 1:
                    self._cn += 1
                    self._namstore(self._cn, seg)
                # Advance to the next line for the nonzero data
                b = self._rdline()
                z  = b if b is not None else ''
                zi = 0
                n, zi = _exindx(z, zi)

            # Process the entry 
            if what >= 4:
                # BOUNDS section: n is the bound-type index (1-based, 1..6)
                if n >= 7:
                    raise RuntimeError(f"bad bound type index {n}")
                if zi >= len(z):
                    b = self._rdline()
                    z  = b if b is not None else ''
                    zi = 0
                col_idx, zi = _exindx(z, zi)
                rownm[0]    = self._namfetch(self._nrow + col_idx)
                if n >= 4:
                    # FR / MI / PL: no numeric value needed
                    # C: n-- >= 4  -> post-decrement; use n-1 as BT index
                    self._emit(
                        f' {BT[n - 1]} {curcol:<8.8}  {rownm[0]:.8}'
                    )
                    continue
                # UP / LO / FX: n decremented to 0-based BT index
                n -= 1
            else:
                # COLUMNS / RHS / RANGES: n is the row index
                rownm[k] = self._namfetch(n)

            # Read the numeric value
            if zi >= len(z):
                b = self._rdline()
                z  = b if b is not None else ''
                zi = 0
            if k:
                rc2, zi = _exform(z, zi, self._ss, self._kmax)
            else:
                rc1, zi = _exform(z, zi, self._ss, self._kmax)

            # Emit the output line(s)
            if what <= 3:
                if self.just1:
                    self._emit(
                        f'    {curcol:<8.8}  {rownm[0]:<8.8}  {rc1:.15}'
                    )
                else:
                    k += 1
                    if k == 1:
                        continue   # wait for a second nonzero on the same line
                    # Two nonzeros on one line (standard MPS compact format)
                    self._emit(
                        f'    {curcol:<8.8}  {rownm[0]:<8.8}  '
                        f'{rc1:<15.15}{rownm[1]:<8.8}  {rc2:.15}'
                    )
                    k = 0
            else:
                # BOUNDS with a value (UP / LO / FX)
                self._emit(
                    f' {BT[n]} {curcol:<8.8}  {rownm[0]:<8.8}  {rc1:.15}'
                )

        # Flush any unpaired pending nonzero
        if k:
            self._emit(
                f'    {curcol:<8.8}  {rownm[0]:<8.8}  {rc1:.15}'
            )


# ---------------------------------------------------------------------------
# Convenience wrappers
# ---------------------------------------------------------------------------

def expand_mps(
    input_file:  "str | TextIO",
    output_file: "str | TextIO | None" = None,
    *,
    keepmyst:   bool          = True,
    blanksubst: Optional[str] = None,
    just1:      bool          = False,
) -> Optional[str]:
    """Expand a compressed netlib LP file to MPS format.

    Parameters
    ----------
    input_file
        Filesystem path (str) or readable file object.
    output_file
        Filesystem path, writable file object, or None.
        When None the MPS text is returned as a string.
    keepmyst
        Include mystery-line extensions in output (default True).
    blanksubst
        Replace blanks in names with this character (e.g. '_').
    just1
        Output at most one nonzero per line.

    Returns
    -------
    MPS text string when output_file is None; otherwise None.

    Examples
    --------
    >>> mps = expand_mps("afiro.mps.netlib")            # returns str
    >>> expand_mps("afiro.mps.netlib", "afiro.mps")     # writes file
    >>> with open("afiro.mps.netlib") as f:
    ...     mps = expand_mps(f)
    """

    return EMPSConverter(
        keepmyst=keepmyst,
        blanksubst=blanksubst,
        just1=just1,
    ).convert(input_file, output_file)


def expand_mps_string(
    compressed_text: str,
    *,
    keepmyst:   bool          = True,
    blanksubst: Optional[str] = None,
    just1:      bool          = False,
) -> str:
    """Expand compressed LP text supplied as a string; return MPS text.

    Examples
    --------
    >>> with open("afiro.mps.netlib") as f:
    ...     raw = f.read()
    >>> mps = expand_mps_string(raw)
    """

    result = expand_mps(
        io.StringIO(compressed_text),
        keepmyst=keepmyst, 
        blanksubst=blanksubst, 
        just1=just1,
    )
    assert result is not None
    return result

def __main():
 
    parser = argparse.ArgumentParser(
        prog='gsimplex-emps',
        description='Expand compressed netlib LP files to MPS format. See also: https://www.netlib.org/lp/data',
    )
    parser.add_argument(
        'files', nargs='*', metavar='FILE',
        help='Compressed input file(s); reads stdin when none given.',
    )
    parser.add_argument(
        '-1', dest='just1', action='store_true',
        help='Output only one nonzero per line.',
    )
    parser.add_argument(
        '-b', dest='blanksubst', action='store_const', const='_', default=None,
        help="Replace blanks within names with '_'.",
    )
    parser.add_argument(
        '-m', dest='keepmyst', action='store_false',
        help='Skip mystery lines.',
    )
    args = parser.parse_args()
 
    conv = EMPSConverter(
        keepmyst=args.keepmyst,
        blanksubst=args.blanksubst,
        just1=args.just1,
    )
 
    if not args.files:
        sys.stdout.write(conv.convert(sys.stdin))   # type: ignore[arg-type]
    else:
        for path in args.files:
            result = conv.convert(path)
            assert result is not None
            sys.stdout.write(result)
 
    return 0

if __name__ == '__main__':
    sys.exit(__main())