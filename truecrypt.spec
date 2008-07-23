#
# Conditional build:
#
%bcond_with	nogui	# build without gui

%define		_wxWid_ver	2.8.7

Summary:	TrueCrypt - Free Open-Source Disk Encryption Software
Summary(pl.UTF-8):	TrueCrypt - wolnodostępne oprogramowanie do szyfrowania dysków
Name:		truecrypt
Version:	6.0a
%define	_rel	0.2
Release:	%{_rel}
License:	TrueCrypt License Version 2.4
Group:		Base/Kernel
#Source0:	http://ftp.uni-kl.de/pub/linux/archlinux/other/truecrypt/TrueCrypt-%{version}-Source.tar.gz
Source0:	http://www.truecrypt.org/downloads/TrueCrypt-%{version}-Source.tar.gz
# Source0-md5:	7281d485a175c161e90526447d9d3fd0
Source1:    http://ftp.wxwidgets.org/pub/%{_wxWid_ver}/wxWidgets-%{_wxWid_ver}.tar.bz2
# Source1-md5:	e3455083afdf6404a569a8bf0701cf13
URL:		http://www.truecrypt.org/
BuildRequires:	gcc	>= 5:4.0.0
BuildRequires:	libfuse-devel
BuildRequires:	rpmbuild(macros) >= 1.379
Requires:	libfuse
Requires:	losetup
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Main Features:
- Creates a virtual encrypted disk within a file and mounts it as a
  real disk.
- Encrypts an entire hard disk partition or a storage device such as
  USB flash drive.
- Encryption is automatic, real-time (on-the-fly) and transparent.
- Provides two levels of plausible deniability, in case an adversary
  forces you to reveal the password:
  1) Hidden volume (steganography).
  2) No TrueCrypt volume can be identified (volumes cannot be
  distinguished from random data).
- Encryption algorithms: AES-256, Blowfish (448-bit key), CAST5,
  Serpent, Triple DES, and Twofish. Mode of operation: LRW (CBC
  supported as legacy).

%description -l pl.UTF-8
Główne cechy:
- Tworzenie wirtualnego szyfrowanego dysku w pliku i montowanie go
  jako prawdziwego dysku.
- Szyfrowanie całej partycji twardego dysku lub urządzenia takiego jak
  dysk flash USB.
- Szyfrowanie automatyczne, w czasie rzeczywistym i przezroczyste.
- Dwa poziomy prawdopodobnych utrudnień, w przypadku, gdy wróg zmusza
  do wyjawienia hasła:
  1) Ukryty wolumen (steganografia).
  2) Żaden wolumen TrueCrypt nie może być zidentyfikowany (wolumeny
  nie dadzą się odróżnić od losowych danych).
- Algorytmy szyfrowania: AES-256, Blowfish (klucz 448-bitowy), CAST5,
  Serpent, Triple DES oraz Twofish. Tryby działania: LRW (CBC
  obsługiwane dla wstecznej kompatybilności).

%prep
%setup -q -a1 -n %{name}-%{version}-source

%build
%if %{with nogui}
%{__make} NOGUI=1 WX_ROOT=%{_builddir}/%{name}-%{version}-source/wxWidgets-%{_wxWid_ver} wxbuild
%{__make} NOGUI=1
%else
%{__make} WX_ROOT=%{_builddir}/%{name}-%{version}-source/wxWidgets-%{_wxWid_ver} wxbuild
%{__make}
%endif

%install
rm -rf $RPM_BUILD_ROOT

install -d $RPM_BUILD_ROOT{/%{_bindir},%{_mandir}/man1}
ls -l Main/truecrypt
install Main/truecrypt $RPM_BUILD_ROOT%{_bindir}/truecrypt
mv -f Release/Setup\ Files/TrueCrypt\ User\ Guide.pdf TrueCrypt-User-Guide.pdf

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%doc License.txt Readme.txt TrueCrypt-User-Guide.pdf
%attr(755,root,root) %{_bindir}/%{name}
##%%{_mandir}/man1/*
