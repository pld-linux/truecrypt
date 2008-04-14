# TODO
# - requires modutils???
# - License: specfile from r1.1 contained different License than GPL
#
# Conditional build:
%bcond_without	dist_kernel	# allow non-distribution kernel
%bcond_without	kernel		# don't build kernel modules
%bcond_without	userspace	# don't build userspace utilities
%bcond_with	verbose		# verbose build (V=1)
#
Summary:	TrueCrypt - Free Open-Source Disk Encryption Software
Summary(pl.UTF-8):	TrueCrypt - wolnodostępne oprogramowanie do szyfrowania dysków
Name:		truecrypt
Version:	4.3a
%define	_rel	0.5
Release:	%{_rel}
License:	GPL
Group:		Base/Kernel
Source0:	http://www.truecrypt.org/downloads/%{name}-%{version}-source-code.tar.gz
# Source0-md5:	8f2536eae16e6044a22b2a82c7003357
Patch0:		%{name}-4.2a_kernel-2.6.18-rc1_fix.patch
Patch1:		%{name}-dm_dev.patch
Patch2:		%{name}-2.6.23.patch
URL:		http://www.truecrypt.org/
BuildRequires:	rpmbuild(macros) >= 1.379
%if %{with kernel}
BuildRequires:	kernel%{_alt_kernel}-module-build >= 3:2.6.20.2
Requires(post,postun):	/sbin/depmod
%endif
Requires:	device-mapper
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

%package -n kernel%{_alt_kernel}-misc-%{name}
Summary:	Linux kernel modules for TrueCrypt
Summary(pl.UTF-8):	Moduły jądra Linuksa dla TrueCrypta
Release:	%{_rel}@%{_kernel_ver_str}
Group:		Base/Kernel
%if %{with dist_kernel}
%requires_releq_kernel
Requires(postun):	%releq_kernel
%endif
Requires:	%{name} = %{version}-%{_rel}
Conflicts:	modutils < 2.4.6-4

%description -n kernel%{_alt_kernel}-misc-%{name}
Linux kernel modules for TrueCrypt.

%description -n kernel%{_alt_kernel}-misc-%{name} -l pl.UTF-8
Moduły jądra Linuksa dla TrueCrypta

%prep
%setup -q -n %{name}-%{version}-source-code
%patch0 -p1
%patch1 -p1
%patch2 -p1

%build
%if %{with kernel}
# kernel module(s)
cd Linux/Kernel
for cfg in %{?with_dist_kernel:dist}%{!?with_dist_kernel:nondist}; do
	if [ ! -r "%{_kernelsrcdir}/config-$cfg" ]; then
		exit 1
	fi
	install -d o/include/linux
	ln -sf %{_kernelsrcdir}/config-$cfg o/.config
	ln -sf %{_kernelsrcdir}/Module.symvers-$cfg o/Module.symvers
	ln -sf %{_kernelsrcdir}/include/linux/autoconf-$cfg.h o/include/linux/autoconf.h
%if %{with dist_kernel}
	%{__make} -j1 -C %{_kernelsrcdir} O=$PWD/o prepare scripts
%else
	install -d o/include/config
	touch o/include/config/MARKER
	ln -sf %{_kernelsrcdir}/scripts o/scripts
%endif
	%{__make} -C %{_kernelsrcdir} clean \
		RCS_FIND_IGNORE="-name '*.ko' -o" \
		M=$PWD O=$PWD/o KSRC=$PWD/o\
		%{?with_verbose:V=1}
	
	%{__make} "KERNEL_SRC=$PWD/o" clean \
		RCS_FIND_IGNORE="-name '*.ko' -o" \
		M=$PWD O=$PWD/o KSRC=$PWD/o \
		%{?with_verbose:V=1}

	%{__make} "KERNEL_SRC=$PWD/o" %{!?with_verbose:NO_WARNINGS=1}
	for i in truecrypt; do
		mv $i{,-$cfg}.ko
	done
done
cd -
%endif

%if %{with userspace}
%{__make} -j1 -C Linux/Cli
%endif

%install
rm -rf $RPM_BUILD_ROOT

%if %{with userspace}
install -d $RPM_BUILD_ROOT{/bin,%{_mandir}/man1}
install Linux/Cli/%{name} $RPM_BUILD_ROOT/bin
install Linux/Cli/Man/%{name}.1 $RPM_BUILD_ROOT%{_mandir}/man1
mv -f Release/Setup\ Files/TrueCrypt\ User\ Guide.pdf TrueCrypt-User-Guide.pdf
%endif

%if %{with kernel}
%install_kernel_modules -m Linux/Kernel/truecrypt -d misc
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%post -n kernel%{_alt_kernel}-misc-%{name}
%depmod %{_kernel_ver}

%postun -n kernel%{_alt_kernel}-misc-%{name}
%depmod %{_kernel_ver}

%if %{with userspace}
%files
%defattr(644,root,root,755)
%doc License.txt Readme.txt TrueCrypt-User-Guide.pdf
%attr(755,root,root) /bin/%{name}
%{_mandir}/man1/*
%endif

%if %{with kernel}
%files -n kernel%{_alt_kernel}-misc-%{name}
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}/misc/*.ko*
%endif
