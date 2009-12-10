#
# Conditional build:
%bcond_without	gui	# build without GUI
%if "%{pld_release}" == "ac"
%bcond_without		gcc4	# use gcc4* packages for building
%else
%bcond_with		gcc4	# use gcc4* packages for building
%endif

%define		wx_ver	2.8.9
Summary:	TrueCrypt - Free Open-Source Disk Encryption Software
Summary(pl.UTF-8):	TrueCrypt - wolnodostępne oprogramowanie do szyfrowania dysków
Name:		truecrypt
Version:	6.3a
Release:	1
License:	TrueCrypt License Version 2.6
Group:		Base/Kernel
# Source download through form from http://www.truecrypt.org/downloads2.php,
# then rename source file (spaces are not allowed in SourceX)
Source0:	TrueCrypt-%{version}-Source.tar.gz
Source1:	http://ftp.wxwidgets.org/pub/%{wx_ver}/wxWidgets-%{wx_ver}.tar.bz2
Source2:	ftp://ftp.rsasecurity.com/pub/pkcs/pkcs-11/v2-20/pkcs11.h
Source3:	ftp://ftp.rsasecurity.com/pub/pkcs/pkcs-11/v2-20/pkcs11f.h
Source4:	ftp://ftp.rsasecurity.com/pub/pkcs/pkcs-11/v2-20/pkcs11t.h
URL:		http://www.truecrypt.org/
BuildRequires:	gcc >= 5:4.0.0
BuildRequires:	libfuse-devel
BuildRequires:	rpm >= 4.4.9-56
BuildRequires:	rpmbuild(macros) >= 1.379
Requires:	losetup
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%if %{with gcc4}
# add suffix, but allow ccache, etc in ~/.rpmmacros
%{expand:%%define	__cc	%(echo '%__cc' | sed -e 's,-gcc,-gcc4,')}
%{expand:%%define	__cxx	%(echo '%__cxx' | sed -e 's,-g++,-g++4,')}
%{expand:%%define	__cpp	%(echo '%__cpp' | sed -e 's,-gcc,-gcc4,')}
%endif

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
%setup -q -n %{name}-%{version}-source -a1
cp %{SOURCE2} %{SOURCE3} %{SOURCE4} .


%build
%if %{without gui}
%{__make} wxbuild \
	CC="%{__cc}" \
	CXX="%{__cxx}" \
	CFLAGS="%{rpmcflags}" \
	CXXFLAGS="%{rpmcxxflags}" \
	NOGUI=1 \
	WX_ROOT=%{_builddir}/%{name}-%{version}-source/wxWidgets-%{wx_ver}
%{__make} \
	NOGUI=1 \
	WXSTATIC=1
%else
%{__make} wxbuild \
	CC="%{__cc}" \
	CXX="%{__cxx}" \
	CFLAGS="%{rpmcflags}" \
	CXXFLAGS="%{rpmcxxflags}" \
	WX_ROOT=%{_builddir}/%{name}-%{version}-source/wxWidgets-%{wx_ver}
%{__make} \
	WXSTATIC=1
%endif

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_bindir},%{_mandir}/man1}

install Main/truecrypt $RPM_BUILD_ROOT%{_bindir}/truecrypt
mv -f Release/Setup\ Files/TrueCrypt\ User\ Guide.pdf TrueCrypt-User-Guide.pdf

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%doc License.txt Readme.txt TrueCrypt-User-Guide.pdf
%attr(755,root,root) %{_bindir}/%{name}
##%%{_mandir}/man1/*
