#
# Conditional build:
%bcond_without	dist_kernel	# allow non-distribution kernel
%bcond_without	kernel		# don't build kernel modules
%bcond_without	smp		# don't build SMP module
%bcond_without	userspace	# don't build userspace module
%bcond_with	verbose		# verbose build (V=1)
#
%ifarch sparc
%undefine	with_smp
%endif
#
%define		snap	-b3
%define		_rel	4
Summary:	Linux driver for WLAN cards based on RT2400
Summary(pl):	Sterownik dla Linuksa do kart bezprzewodowych opartych na uk³adzie RT2400
Name:		rt2400
Version:	1.2.2
Release:	%{_rel}
License:	GPL v2
Group:		Base/Kernel
Source0:	http://dl.sourceforge.net/rt2400/%{name}-%{version}%{snap}.tar.gz
# Source0-md5:	333bf6d7fa81a6d78c72aad6a48e9bc3
URL:		http://rt2x00.serialmonkey.com/
%if %{with kernel}
%{?with_dist_kernel:BuildRequires:	kernel-module-build >= 3:2.6.7}
BuildRequires:	rpmbuild(macros) >= 1.153
%endif
%if %{with userspace}
BuildRequires:	pkgconfig
BuildRequires:	qmake
BuildRequires:	qt-devel >= 6:3.1.1
%endif
BuildRequires:	perl-base
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
A configuartion tool for WLAN cards based on RT2400.

%description -l pl
Program do konfiguracji kart bezprzewodowych opartych na uk³adzie
RT2400.

%package -n kernel-net-rt2400
Summary:	Linux driver for WLAN cards based on RT2400
Summary(pl):	Sterownik dla Linuksa do kart bezprzewodowych opartych na uk³adzie RT2400
Release:	%{_rel}@%{_kernel_ver_str}
Group:		Base/Kernel
%{?with_dist_kernel:%requires_releq_kernel_up}
Requires(post,postun):	/sbin/depmod
%{?with_dist_kernel:Requires(postun):	kernel}

%description -n kernel-net-rt2400
This is a Linux driver for WLAN cards based on RT2400.

This package contains Linux module.

%description -n kernel-net-rt2400 -l pl
Sterownik dla Linuksa do kart bezprzewodowych opartych na uk³adzie
RT2400.

Ten pakiet zawiera modu³ j±dra Linuksa.

%package -n kernel-smp-net-rt2400
Summary:	Linux SMP driver for WLAN cards based on RT2400
Summary(pl):	Sterownik dla Linuksa SMP do kart bezprzewodowych opartych na uk³adzie RT2400
Release:	%{_rel}@%{_kernel_ver_str}
Group:		Base/Kernel
%{?with_dist_kernel:%requires_releq_kernel_smp}
Requires(post,postun):	/sbin/depmod
%{?with_dist_kernel:Requires(postun):	kernel-smp}

%description -n kernel-smp-net-rt2400
This is a Linux driver for WLAN cards based on RT2400.

This package contains Linux SMP module.

%description -n kernel-smp-net-rt2400 -l pl
Sterownik dla Linuksa do kart bezprzewodowych opartych na uk³adzie
RT2400.

Ten pakiet zawiera modu³ j±dra Linuksa SMP.

%prep
%setup -q -n %{name}-%{version}%{snap}

#%{__perl} -pi -e 's@/lib@/%{_lib}@g' Utility/Makefile

%build
%if %{with userspace}
cd Utility
qmake -o Makefile.orig raconfig2400.pro
sed -e 's/-lqt /-lqt-mt /g' Makefile.orig > Makefile
%{__make} \
        CXXFLAGS="%{rpmcflags} %(pkg-config qt-mt --cflags)" \
        LDFLAGS="%{rpmldflags}" \
        QTDIR="%{_prefix}"
cd ..
%endif

%if %{with kernel}
%ifarch sparc
	# workaround for (probably GCC) bug on sparc:
	# `unable to find a register to spill in class `FP_REGS''
	BUGFLAGS="-fno-schedule-insns"
%else
	BUGFLAGS=
%endif
# kernel module(s)
cd Module
for cfg in %{?with_dist_kernel:%{?with_smp:smp} up}%{!?with_dist_kernel:nondist}; do
	if [ ! -r "%{_kernelsrcdir}/config-$cfg" ]; then
		exit 1
	fi
	install -d o/include/linux
	ln -sf %{_kernelsrcdir}/config-$cfg o/.config
	ln -sf %{_kernelsrcdir}/Module.symvers-$cfg o/Module.symvers
	ln -sf %{_kernelsrcdir}/include/linux/autoconf-$cfg.h o/include/linux/autoconf.h
%if %{with dist_kernel}
	%{__make} -C %{_kernelsrcdir} O=$PWD/o prepare scripts
%else
	install -d o/include/config
	touch o/include/config/MARKER
	ln -sf %{_kernelsrcdir}/scripts o/scripts
%endif
	%{__make} -C %{_kernelsrcdir} clean \
		RCS_FIND_IGNORE="-name '*.ko' -o" \
		SYSSRC=%{_kernelsrcdir} \
		SYSOUT=$PWD/o \
		M=$PWD O=$PWD/o \
		%{?with_verbose:V=1}
	%{__make} -C %{_kernelsrcdir} modules \
		CC="%{__cc} $BUGFLAGS" CPP="%{__cpp}" \
		SYSSRC=%{_kernelsrcdir} \
		SYSOUT=$PWD/o \
		M=$PWD O=$PWD/o \
		%{?with_verbose:V=1}
	mv rt2400{,-$cfg}.ko
done
cd -
%endif

%install
rm -rf $RPM_BUILD_ROOT

%if %{with userspace}
install -D Utility/RaConfig2400 $RPM_BUILD_ROOT%{_bindir}/RaConfig2400
%endif

%if %{with kernel}
cd Module
install -d $RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}{,smp}/kernel/drivers/net/wireless
install rt2400-%{?with_dist_kernel:up}%{!?with_dist_kernel:nondist}.ko \
	$RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}/kernel/drivers/net/wireless/rt2400.ko
%if %{with smp} && %{with dist_kernel}
install rt2400-smp.ko \
	$RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}smp/kernel/drivers/net/wireless/rt2400.ko
%endif
cd -
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%post -n kernel-net-rt2400
%depmod %{_kernel_ver}

%postun -n kernel-net-rt2400
%depmod %{_kernel_ver}

%post -n kernel-smp-net-rt2400
%depmod %{_kernel_ver}smp

%postun -n kernel-smp-net-rt2400
%depmod %{_kernel_ver}smp

%if %{with userspace}
%files
%defattr(644,root,root,755)
%doc CHANGELOG FAQ
%attr(755,root,root) %{_bindir}/RaConfig2400
%endif

%if %{with kernel}
%files -n kernel-net-rt2400
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}/kernel/drivers/net/wireless/*.ko*

%if %{with smp} && %{with dist_kernel}
%files -n kernel-smp-net-rt2400
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}smp/kernel/drivers/net/wireless/*.ko*
%endif
%endif
