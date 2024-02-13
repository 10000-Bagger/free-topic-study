# Multitenant Architecture and CDB/PDB

## 요약:

Oracle은 Multitenant Architecture를 지원하기 위해 CDB와 PDB 구조를 가지고 있으며, Oracle Database 21c 버전부터는 multitenant container database만을 지원한다. 그 때문에 최신 버전의 Oracle Database를 사용하기 위해서는 알아둬야하는 구조.

![CDB, PDB 설명 - COMPLEX 버전](/hong/img/CDB-PDB-complex-version.png)
_CDB와 PDB를 설명하는 예시_

### 용어 설명:

- **Multitenant Architecture**: 여러 사용자 그룹이 통합된 하나의 DB instance를 사용하는 구조.

- **CDB**: Container Database

- **PDB**: Pluggable Database

## Single-tenant vs Multi-tenant

![CDB, PDB 설명 - COMPLEX 버전](/hong/img/Single-tenant-Multy-tenat-33.png)

### Single-tenant architecture란?

Single-tenant architecture는 하나의 앱 서비스를 서빙할 때 그 서비스만을 위한 infrastructure, hardware, software ecosystem 등을 사용하는 구조이다. 만약 10개의 독립적인 앱 서비스가 있다고 가정한다면, 10개의 독립적인 환경을 구축해야 함을 의미한다. 이는 독립적인 서비스가 많아질수록 비용, 유지보수에 들어가는 노력, 시스템 복잡도 모두 증가하는 문제가 있다.

### Multi-tenant architecture란?

Multi-tenant architecture는 한 환경 또는 모델을 사용하여 여러 개의 독립적인 서비스를 한정된 자원 안에서 확장성(scalable) 있고 탄력적(resilient)으로 지원하기 위해 고안되었다. 이 구조에서 데이터는 통합적으로 관리되고, 독립적인 서비스들은 공유된 인프라를 사용한다. 하지만, 데이터베이스는 논리적으로 완전히 분리되어 있기 때문에 목적에 따라 서비스의 변경, 추가, 삭제가 용이하다.

multi-tenent에 적합한 대표적인 서비스: Atlassian, Salesforce의 SaaS applications

### Container Database란?

> Container databases group multiple databases together to share common features.

이름 그대로 여러 Pluggable Database를 하나로 묶어주는 container database이다. 따라서 CDB는 사용자가 생성한 여러 개의 PDB의 묶음이라고 생각하면 된다. (0 to many 관계)

Oracle database를 서버에 설치해서 기동해 보면 하나의 instance를 운용하기 위한 수많은 프로세스가 떠 있는 것을 확인할 수 있다. 이런 프로세스 중 공통으로 사용될 수 있는 기능들을 묶어주고, 자원을 공유하는 방식으로 DB 효율을 높인다. 또한, 여러 개의 virtual machine에서 각각의 database를 관리하는 방식보다 관리 측면에서 높은 효율을 가져갈 수 있다.

### Pluggable Database란?

> A PDB is a user-created set of schemas, objects, and related structures that appears logically to a client application as a separate database.

PDB는 사용자가 생성한 스키마, 객체, 관련 구조들의 집합으로, 클라이언트 애플리케이션에는 논리적으로 구분되는 별도의 데이터베이스로 보이는 것이다 (이는 CDB에 속해있는 하나의 DB임.) 이런 PDB들은 각각의 서비스를 위한 DB로 사용된다.

![CDB, PDB 설명 - SIMPLE 버전](/hong/img/CDB-PDB-simple-version.png)

_CDB와 PDB를 설명하는 간단한 예시_

정리해 보면,

1. 하나의 CDB root container를 생성하고,
2. CDB에서 template으로 사용할 Seed PDB를 생성하고,
3. Seed PDB를 복제하여 사용자가 원하는 PDB를 생성한다 (생성된 PDB들은 각각의 서비스를 위한 DB로 사용된다.)
4. 각각의 PDB들은 독립적으로 관리되며, CDB의 자원을 공유한다.

이런 방식으로 Database Administrator는 필요에 따라 PDB를 생성, 삭제하고, CDB를 통해 PDB들을 공유 자원을 관리할 수 있다. 또한, 관리자가 원한다면 Application Root를 추가하는 방식으로 서비스를 여러 layer로 나눠 PDBs를 구분하여 운영할 수도 있다.

### 정리: 그래서 왜 사용?

- **More efficient use of resources**: 효율적인 서버 자원 사용 가능. 10개 서비스를 위해 10개의 DB 서버를 구동할 경우, 각각의 서버 CPU, Memory 사용량에 여유분을 준비해야 한다. 이유는 자원을 100% 다 쓰게 되면 시스템이 서버리거나 느려지기 때문에 만일의 사태에 대비해서 충분한 자원을 준비해 둬야 하기 때문이다. CDB를 사용하면 서비스들이 전체 자원을 공유하기 때문에 서비스마다 여유분을 고려할 필요가 없고 전체 사용량을 기준으로 적당한 여유 자원을 준비할 수 있다.
- **Easier duplication and access across resources**: PDB를 사용하면, 쉽게 PDB를 복제해서 테스트 또는 개발 DB로 사용할 수 있다. 또한, Atlassian과 같이 많은 SaaS 서비스을 회사마다 독립적으로 관리해야 하고, 서비스끼리 통합된 데이터를 공유해야 할 경우, 이런 multi-tenant 구조 사용이 적합하다 ([참고](https://www.atlassian.com/trust/reliability/cloud-architecture-and-operational-practices#distributed-services-architecture))
- **Portability**: 기존 버전의 Oracle Database를 unplug하고, 최신 버전의 Oracle DB를 plug 하여 빠르고 독립적으로 DB 업그레이드가 가능하다. 특정 서비스를 종료시키거나 새로운 서비스를 추가하는 작업 또한 쉽게 가능하며, 플랫폼에 연결된 후 곧바로 다른 서비스들과 통합된 서비스를 제공할 수 있다.
- **Easier to administrate, including user and admin controls**: 패치, 백업 등 관리가 수월함. 시스템상으로는 1개의 DB이기 때문에 패치, 백업 등의 작업을 1번만 해주면 끝.

## References:

Multi tenant Architecture for a SaaS Application on AWS: https://www.clickittech.com/saas/multi-tenant-architecture/

Database Concepts: 2. CDBs and PDBs: https://docs.oracle.com/en/database/oracle/oracle-database/21/cncpt/CDBs-and-PDBs.html#GUID-5C339A60-2163-4ECE-B7A9-4D67D3D894FB

What is a Container Database?: https://developer.oracle.com/en/learn/technical-articles/what-is-a-container-database

Oracle Database의 Multitenant 사용 예제: https://oracle-base.com/articles/12c/multitenant-overview-container-database-cdb-12cr1
