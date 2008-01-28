#
# Conditional build:
%bcond_without	dist_kernel	# allow non-distribution kernel
%bcond_without	kernel		# don't build kernel modules
%bcond_without	up		# don't build UP module
%bcond_without	smp		# don't build SMP module
%bcond_without	userspace	# don't build userspace module
%bcond_with	verbose		# verbose build (V=1)
%bcond_with	grsec_kernel	# build for kernel-grsecurity

%ifarch sparc
%undefine	with_smp
%endif

%if %{without kernel}
%undefine	with_dist_kernel
%endif
%if %{with kernel} && %{with dist_kernel} && %{with grsec_kernel}
%define	alt_kernel	grsecurity
%endif
%if "%{_alt_kernel}" != "%{nil}"
%undefine	with_userspace
%endif

%define		snap	-cvs-20060911
%define		_rel	60
%define		pname	rt2400
Summary:	Linux driver for WLAN cards based on RT2400
Summary(pl):	Sterownik dla Linuksa do kart bezprzewodowych opartych na uk³adzie RT2400
Name:		%{pname}%{_alt_kernel}
Version:	1.2.2
Release:	%{_rel}
License:	GPL v2
Group:		Base/Kernel
# Source0:	http://dl.sourceforge.net/rt2400/%{pname}-%{version}%{snap}.tar.gz
Source0:	%{pname}-%{version}%{snap}.tar.bz2
# Source0-md5:	5a0c2c65af1364b215d56be2b881e24f
URL:		http://rt2x00.serialmonkey.com/
%if %{with kernel}
%{?with_dist_kernel:BuildRequires:	kernel%{_alt_kernel}-module-build >= 3:2.6.7}
BuildRequires:	rpmbuild(macros) >= 1.330
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

%package -n kernel%{_alt_kernel}-net-rt2400
Summary:	Linux driver for WLAN cards based on RT2400
Summary(pl):	Sterownik dla Linuksa do kart bezprzewodowych opartych na uk³adzie RT2400
Release:	%{_rel}@%{_kernel_ver_str}
Group:		Base/Kernel
%{?with_dist_kernel:%requires_releq_kernel_up}
Requires(post,postun):	/sbin/depmod

%description -n kernel%{_alt_kernel}-net-rt2400
This is a Linux driver for WLAN cards based on RT2400.

This package contains Linux module.

%description -n kernel%{_alt_kernel}-net-rt2400 -l pl
Sterownik dla Linuksa do kart bezprzewodowych opartych na uk³adzie
RT2400.

Ten pakiet zawiera modu³ j±dra Linuksa.

%package -n kernel%{_alt_kernel}-smp-net-rt2400
Summary:	Linux SMP driver for WLAN cards based on RT2400
Summary(pl):	Sterownik dla Linuksa SMP do kart bezprzewodowych opartych na uk³adzie RT2400
Release:	%{_rel}@%{_kernel_ver_str}
Group:		Base/Kernel
%{?with_dist_kernel:%requires_releq_kernel_smp}
Requires(post,postun):	/sbin/depmod

%description -n kernel%{_alt_kernel}-smp-net-rt2400
This is a Linux driver for WLAN cards based on RT2400.

This package contains Linux SMP module.

%description -n kernel%{_alt_kernel}-smp-net-rt2400 -l pl
Sterownik dla Linuksa do kart bezprzewodowych opartych na uk³adzie
RT2400.

Ten pakiet zawiera modu³ j±dra Linuksa SMP.

%prep
%setup -q -n %{pname}-%{version}%{snap}

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
%build_kernel_modules -C Module -m rt2400 \
%ifarch sparc
	EXTRA_CFLAGS="-fno-schedule-insns"
	# workaround for (probably GCC) bug on sparc:
	# `unable to find a register to spill in class `FP_REGS''
%else
	# beware of evil '\'
%endif
%endif

%install
rm -rf $RPM_BUILD_ROOT

%if %{with userspace}
install -D Utility/RaConfig2400 $RPM_BUILD_ROOT%{_bindir}/RaConfig2400
%endif

%if %{with kernel}
cd Module
%install_kernel_modules -m rt2400 -d kernel/drivers/net/wireless
cd -
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%post -n kernel%{_alt_kernel}-net-rt2400
%depmod %{_kernel_ver}

%postun -n kernel%{_alt_kernel}-net-rt2400
%depmod %{_kernel_ver}

%post -n kernel%{_alt_kernel}-smp-net-rt2400
%depmod %{_kernel_ver}smp

%postun -n kernel%{_alt_kernel}-smp-net-rt2400
%depmod %{_kernel_ver}smp

%if %{with userspace}
%files
%defattr(644,root,root,755)
%doc CHANGELOG FAQ
%attr(755,root,root) %{_bindir}/RaConfig2400
%endif

%if %{with kernel}
%if %{with up} || %{without dist_kernel}
%files -n kernel%{_alt_kernel}-net-rt2400
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}/kernel/drivers/net/wireless/*.ko*
%endif

%if %{with smp} && %{with dist_kernel}
%files -n kernel%{_alt_kernel}-smp-net-rt2400
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}smp/kernel/drivers/net/wireless/*.ko*
%endif
%endif
