# Conditional build:
%bcond_without	dist_kernel	# allow non-distribution kernel
%bcond_without	kernel		# don't build kernel modules
%bcond_without	smp		# don't build SMP module
%bcond_with	verbose		# verbose build (V=1)

Summary:	TrueCrypt - Free Open-Source Disk Encryption Software
#Summary(pl):	
Name:		truecrypt
Version:	4.2a
Release:	0.2
License:	GPL
Group:		Base/Kernel
Source0:	%{name}-%{version}-source-code.tar.gz
Patch0:		%{name}-build.patch
Patch1:		%{name}-4.2a_kernel-2.6.18-rc1_fix.patch
URL:		http://www.truecrypt.org
%if %{with kernel}
Requires(post,postun):	/sbin/depmod
%endif
Requires:	device-mapper
Requires:	losetup
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Main Features:

* Creates a virtual encrypted disk within a file and mounts it as a real disk.
* Encrypts an entire hard disk partition or a storage device such as USB flash drive.
* Encryption is automatic, real-time (on-the-fly) and transparent.
* Provides two levels of plausible deniability, in case an adversary forces you to reveal the password:
  1) Hidden volume (steganography ? more information may be found here).
  2) No TrueCrypt volume can be identified (volumes cannot be distinguished from random data).
* Encryption algorithms: AES-256, Blowfish (448-bit key), CAST5, Serpent, Triple DES, and Twofish.
  Mode of operation: LRW  (CBC supported as legacy).

%description -l pl

%package -n kernel%{_alt_kernel}-misc-%{name}
Summary:	Kernel modules for %{name}
Summary(pl):	Modu³y j±dra dla programu %{name}
Release:	%{release}@%{_kernel_ver_str}
Group:		base/kernel
%if %{with dist_kernel}
%requires_releq_kernel_up
Requires(postun):       %releq_kernel_up
%endif
Requires:	%{name} = %{version}
Requires:	modutils >= 2.4.6-4

%description -n kernel%{_alt_kernel}-misc-%{name}

%package -n kernel%{_alt_kernel}-smp-misc-%{name}
Summary:	Kernel SMP modules for %{name}
Summary(pl):	Modu³y SMP j±dra dla programu %{name}
Release:	%{release}
Group:		base/kernel
%if %{with dist_kernel}
%requires_releq_kernel_smp
Requires(postun):       %releq_kernel_smp
%endif
Requires:	%{name} = %{version}
Requires:	modutils >= 2.4.6-4

%description -n kernel%{_alt_kernel}-smp-misc-%{name}

%prep
%setup -q
%patch0 -p1
%patch1 -p1

%build
# kernel module(s)
cd Linux/Kernel
for cfg in %{?with_dist_kernel:%{?with_smp:smp} up}%{!?with_dist_kernel:nondist}; do
	if [ ! -r "%{_kernelsrcdir}/config-$cfg" ]; then
		exit 1
	fi
	install -d o/include/linux
	ln -sf %{_kernelsrcdir}/config-$cfg o/.config
	ln -sf %{_kernelsrcdir}/Module.symvers-$cfg o/Module.symvers
	ln -sf %{_kernelsrcdir}/include/linux/autoconf-$cfg.h o/include/linux/autoconf.h
	install -d o/drivers
	ln -sf %{_kernelsrcdir}/drivers/md o/drivers
	#ln -sf %{_kernelsrcdir}/Makefile o/Makefile
%if %{with dist_kernel}
	%{__make} -C %{_kernelsrcdir} O=$PWD/o prepare scripts
%else
	install -d o/include/config
	touch o/include/config/MARKER
	ln -sf %{_kernelsrcdir}/scripts o/scripts
%endif
	%{__make} -C %{_kernelsrcdir} clean \
		RCS_FIND_IGNORE="-name '*.ko' -o" \
		M=$PWD O=$PWD/o KSRC=$PWD/o\
		%{?with_verbose:V=1}
	cd ..
	./build.sh $PWD/Kernel/o
	for i in truecrypt; do
		mv Kernel/$i{,-$cfg}.ko
	done
	cd -
done

%install
rm -rf $RPM_BUILD_ROOT

install -d $RPM_BUILD_ROOT/bin $RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}{,smp}/misc
install Linux/Cli/%{name} $RPM_BUILD_ROOT/bin
install -d $RPM_BUILD_ROOT/%{_mandir}/man1
install Linux/Cli/Man/%{name}.1 $RPM_BUILD_ROOT/%{_mandir}/man1

for i in truecrypt; do
install Linux/Kernel/$i-%{?with_dist_kernel:up}%{!?with_dist_kernel:nondist}.ko \
	$RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}/misc/$i.ko
done
%if %{with smp} && %{with dist_kernel}
for i in truecrypt; do
install Linux/Kernel/$i-smp.ko \
	$RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}smp/misc/$i.ko
done
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%post -n kernel%{_alt_kernel}-misc-%{name}
%depmod %{_kernel_ver}

%postun -n kernel%{_alt_kernel}-misc-%{name}
%depmod %{_kernel_ver}

%post -n kernel%{_alt_kernel}-smp-misc-%{name}
%depmod %{_kernel_ver}smp

%postun -n kernel%{_alt_kernel}-smp-misc-%{name}
%depmod %{_kernel_ver}smp


%files
%defattr(644,root,root,755)
%doc License.txt Readme.txt
%attr(755,root,root) /bin/%{name}
%{_mandir}/man1/*

%files -n kernel%{_alt_kernel}-misc-%{name}
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}/misc/*

%files -n kernel%{_alt_kernel}-smp-misc-%{name}
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}smp/misc/*
