#
# TODO
#		- utility subpkg.
#
# Conditional build:
%bcond_without	dist_kernel	# allow non-distribution kernel
%bcond_without	kernel		# don't build kernel modules
%bcond_without	smp		# don't build SMP module
%bcond_without	userspace	# don't build userspace module
%bcond_with	verbose		# verbose build (V=1)
#
Summary:	Linux driver for WLAN card base on RT2400
Summary(pl):	Sterownik dla Linuksa do kart bezprzewodowych na uk³adzie RT2400
Name:		kernel-net-rt2400
Version:	1.2.0
%define		_rel	0.1
Release:	%{_rel}@%{_kernel_ver_str}
Group:		Base/Kernel
License:	MPL or GPL
# Source0:	http://www.minitar.com/downloads/rt2400_linux-%{version}-b1.tgz
Source0:	http://dl.sf.net/rt2400/rt2400-%{version}.tar.gz
# Source0-md5:  d107a738db2cc0c06a6f400d9948fc73
# URL:		http://www.minitar.com/
URL:		http://rt2400.sourceforge.net/
%if %{with kernel}
%{?with_dist_kernel:BuildRequires:	kernel-module-build >= 2.6.7}
BuildRequires:	rpmbuild(macros) >= 1.153
%endif
%{?with_dist_kernel:%requires_releq_kernel_up}
Requires(post,postun):	/sbin/depmod
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description -n kernel-net-rt2400
This is driver for WLAN card based on RT2400 for Linux.

This package contains Linux module.

%description -n kernel-net-rt2400 -l pl
Sterownik dla Linuksa do kart WLAN opartych o uk³ad RT2400.

Ten pakiet zawiera modu³ j±dra Linuksa.

%package -n kernel-smp-net-rt2400
Summary:	Linux SMP driver for WLAN card base on RT2400
Summary(pl):	Sterownik dla Linuksa SMP do kart bezprzewodowych na uk³adzie RT2400
Release:	%{_rel}@%{_kernel_ver_str}
Group:		Base/Kernel
%{?with_dist_kernel:%requires_releq_kernel_smp}
Requires(post,postun):	/sbin/depmod

%description -n kernel-smp-net-rt2400
This is driver for WLAN card based on RT2400 for Linux.

This package contains Linux SMP module.

%description -n kernel-smp-net-rt2400 -l pl
Sterownik dla Linuksa do kart WLAN opartych o uk³ad RT2400.

Ten pakiet zawiera modu³ j±dra Linuksa SMP.

%prep
%setup -q -n rt2400-%{version}

%build
%if %{with kernel}
# kernel module(s)
cd Module
for cfg in %{?with_dist_kernel:%{?with_smp:smp} up}%{!?with_dist_kernel:nondist}; do
    if [ ! -r "%{_kernelsrcdir}/config-$cfg" ]; then
	exit 1
    fi
    rm -rf include
    install -d include/{linux,config}
    ln -sf %{_kernelsrcdir}/config-$cfg .config
    ln -sf %{_kernelsrcdir}/include/linux/autoconf-$cfg.h include/linux/autoconf.h
    ln -sf %{_kernelsrcdir}/include/asm-%{_target_base_arch} include/asm
    touch include/config/MARKER
    %{__make} -C %{_kernelsrcdir} clean \
	RCS_FIND_IGNORE="-name '*.ko' -o" \
	M=$PWD O=$PWD \
	%{?with_verbose:V=1}
    %{__make} -C %{_kernelsrcdir} modules \
	M=$PWD O=$PWD \
	%{?with_verbose:V=1}
    mv rt2400{,-$cfg}.ko
done
cd -
%endif

%install
rm -rf $RPM_BUILD_ROOT

%if %{with kernel}
cd Module
install -d $RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}{,smp}/drivers/net/wireless
install rt2400-%{?with_dist_kernel:up}%{!?with_dist_kernel:nondist}.ko \
	$RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}/drivers/net/wireless/rt2400.ko
%if %{with smp} && %{with dist_kernel}
install rt2400-smp.ko \
	$RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}smp/drivers/net/wireless/rt2400.ko
%endif
cd -
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%post
%depmod %{_kernel_ver}

%postun
%depmod %{_kernel_ver}

%post -n kernel-smp-net-rt2400
%depmod %{_kernel_ver}

%postun -n kernel-smp-net-rt2400
%depmod %{_kernel_ver}

%if %{with kernel}
%files -n kernel-net-rt2400
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}/drivers/net/wireless/*.ko*

%if %{with smp} && %{with dist_kernel}
%files -n kernel-smp-net-rt2400
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}smp/drivers/net/wireless/*.ko*
%endif
%endif
