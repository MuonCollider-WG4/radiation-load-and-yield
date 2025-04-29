*                                                                      *
*=== mgdraw ===========================================================*
*                                                                      *
      SUBROUTINE MGDRAW ( ICODE, MREG )

      INCLUDE 'dblprc.inc'
      INCLUDE 'dimpar.inc'
      INCLUDE 'iounit.inc'
*
*----------------------------------------------------------------------*
*                                                                      *
*     Copyright (C) 2025:  CERN                                        *
*     All Rights Reserved.                                             *
*                                                                      *
*----------------------------------------------------------------------*
*
      INCLUDE 'caslim.inc'
      INCLUDE 'comput.inc'
      INCLUDE 'sourcm.inc'
      INCLUDE 'fheavy.inc'
      INCLUDE 'flkstk.inc'
      INCLUDE 'genstk.inc'
      INCLUDE 'mgddcm.inc'
      INCLUDE 'paprop.inc'
      INCLUDE 'quemgd.inc'
      INCLUDE 'sumcou.inc'
      INCLUDE 'trackr.inc'
      INCLUDE 'flkmat.inc'
*
*
      LOGICAL LFCOPE
      CHARACTER*8 NRGNAM, MRGNAM
      SAVE LFCOPE
      DATA LFCOPE / .FALSE. /
      LOGICAL INGEO
      INTEGER NRGMAT, OLDMAT
      
      IF ( .NOT. LFCOPE ) THEN
         LFCOPE = .TRUE.
         WRITE(99,9998) "# ID", "E_kin[GeV]", 
     &        "x[cm]", "y[cm]", "z[cm]",
     &        "cx[-]", "cy[-]", "cz[-]"
      END IF
 9998 FORMAT (A4,7A15)
      RETURN

      ! Boundary crossing: our interest
      ENTRY BXDRAW ( ICODE, MREG, NEWREG, XSCO, YSCO, ZSCO )
      CALL GEOR2N ( MREG,   MRGNAM, IERR1 )
      CALL GEOR2N ( NEWREG, NRGNAM, IERR2 )
      IF ( NRGNAM .EQ. 'VcR1' ) THEN
         EKIN = ETRACK-AM(JTRACK)
         WRITE(99, 9999) JTRACK, ETRACK-AM(JTRACK), 
     &        XSCO, YSCO, ZSCO,
     &        CXTRCK, CYTRCK, CZTRCK
      END IF   
      RETURN
 9999 FORMAT (I2,7E15.7) 

      ! Empty entries, not used
      ENTRY EEDRAW ( ICODE )
      RETURN

      ENTRY ENDRAW ( ICODE, MREG, RULL, XSCO, YSCO, ZSCO )
      RETURN
      
      ENTRY SODRAW
      RETURN
      
      ENTRY USDRAW ( ICODE, MREG, XSCO, YSCO, ZSCO )
      RETURN
*=== End of subrutine Mgdraw ==========================================*
      END

