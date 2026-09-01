#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/stream/EDProducer.h"
#include "FWCore/Framework/interface/MakerMacros.h"

#include "FWCore/Framework/interface/Event.h"
#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "FWCore/ParameterSet/interface/ConfigurationDescriptions.h"
#include "FWCore/ParameterSet/interface/ParameterSetDescription.h"

#include "SimDataFormats/CaloHit/interface/PCaloHit.h"
#include "SimDataFormats/CaloHit/interface/PCaloHitContainer.h"
#include "SimDataFormats/CaloTest/interface/HGCalTestNumbering.h"
#include "Geometry/HcalCommonData/interface/HcalHitRelabeller.h"
#include "Geometry/Records/interface/CaloGeometryRecord.h"
#include "DataFormats/L1THGCal/interface/HGCalTriggerCell.h"
#include "DataFormats/L1THGCal/interface/HGCalMulticluster.h"
#include "DataFormats/Common/interface/AssociationMap.h"
#include "DataFormats/Common/interface/OneToMany.h"
#include "SimDataFormats/CaloAnalysis/interface/CaloParticleFwd.h"
#include "SimDataFormats/CaloAnalysis/interface/CaloParticle.h"
#include "DataFormats/ForwardDetId/interface/HGCalTriggerDetId.h"
#include "DataFormats/ForwardDetId/interface/HGCalTriggerModuleDetId.h"
#include "DataFormats/ForwardDetId/interface/HGCEEDetId.h"
#include "L1Trigger/L1THGCal/interface/HGCalTriggerGeometryBase.h"
#include "L1Trigger/L1THGCalUtilities/interface/HGCalTriggerNtupleBase.h"
#include "L1Trigger/L1THGCal/interface/HGCalTriggerTools.h"
#include "DataFormats/NanoAOD/interface/FlatTable.h"
#include "SimDataFormats/CaloAnalysis/interface/SimCluster.h"
#include "SimDataFormats/Track/interface/SimTrack.h"
#include "SimDataFormats/Vertex/interface/SimVertex.h"

#include "MagneticField/Records/interface/IdealMagneticFieldRecord.h"
#include "MagneticField/Engine/interface/MagneticField.h"
#include "CommonTools/BaseParticlePropagator/interface/RawParticle.h"
#include "CommonTools/BaseParticlePropagator/interface/BaseParticlePropagator.h"
#include "CaloML/SimTruth/interface/util.h"

#include "CaloML/DataFormats/interface/HGCWaferInfo.h"
#include "CaloML/DataFormats/interface/HitTruthInfo.h"

#include "L1Trigger/L1THGCal/interface/concentrator/AEinputUtil.h"

class HGCWaferInfoTableProducer : public edm::stream::EDProducer<> {
public:
    explicit HGCWaferInfoTableProducer(const edm::ParameterSet&);

    void produce(edm::Event&, const edm::EventSetup&) override;
    static void fillDescriptions(edm::ConfigurationDescriptions& descriptions);

    // beginRun() to get geometry and initialize trigger tools
    void beginRun(const edm::Run& run, const edm::EventSetup& es) override;

private:
    edm::EDGetToken TCs_token_;
    edm::EDGetToken TCtruth_token_;
    edm::EDGetToken waferinfo_token_;

    int verbose_;

    const edm::ESGetToken<HGCalTriggerGeometryBase, CaloGeometryRecord> geomToken_;
    HGCalTriggerTools triggerTools_;

    unsigned bitsPerADC_;
    unsigned bitsPerNorm_;
    unsigned bitsPerCALQ_;
    unsigned bitsPerInput_;
  
    bool useModuleFactor_;
    bool bitShiftNormalize_;
    bool useTransverseADC_;
    bool normByMax_;
  
    AEinputUtil aeInputUtil_;

    std::string name_;
    std::string tctablename_;

    int findTheWaferIndex(const std::vector<CaloML::HGCWaferInfo>& waferInfos, unsigned tcid) {
        unsigned target_waferID = triggerTools_.getTriggerGeometry()->getModuleFromTriggerCell(tcid);

        for (size_t i = 0; i < waferInfos.size(); ++i) {
            if (waferInfos[i].waferID == target_waferID) {
                return i;
            }
        }
        return -1; // not found
    }
};

HGCWaferInfoTableProducer::HGCWaferInfoTableProducer(const edm::ParameterSet& conf) :
    TCs_token_(consumes<edm::View<l1t::HGCalTriggerCell>>(conf.getParameter<edm::InputTag>("TCs"))),
    TCtruth_token_(consumes<edm::View<CaloML::HitTruthInfo>>(conf.getParameter<edm::InputTag>("TCtruth"))),
    waferinfo_token_(consumes<std::vector<CaloML::HGCWaferInfo>>(conf.getParameter<edm::InputTag>("waferInfo"))),
    verbose_(conf.getParameter<int>("verbose")),
    geomToken_(edm::stream::EDProducer<>::esConsumes<edm::Transition::BeginRun>()),
    bitsPerADC_(conf.getParameter<unsigned>("bitsPerADC")),
    bitsPerNorm_(conf.getParameter<unsigned>("bitsPerNorm")),
    bitsPerCALQ_(conf.getParameter<unsigned>("bitsPerCALQ")),
    bitsPerInput_(conf.getParameter<unsigned>("bitsPerInput")),
    useModuleFactor_(conf.getParameter<bool>("useModuleFactor")),
    bitShiftNormalize_(conf.getParameter<bool>("bitShiftNormalize")),
    useTransverseADC_(conf.getParameter<bool>("useTransverseADC")),
    normByMax_(conf.getParameter<bool>("normByMax")),
    aeInputUtil_(bitsPerADC_, bitsPerNorm_, bitsPerCALQ_, bitsPerInput_, useModuleFactor_, bitShiftNormalize_, useTransverseADC_, normByMax_),
    name_(conf.getParameter<std::string>("name")),
    tctablename_(conf.getParameter<std::string>("tctablename"))
{
    produces<nanoaod::FlatTable>("wafers");
    produces<nanoaod::FlatTable>("TCassociation");
    produces<nanoaod::FlatTable>("ECONinputs");
    produces<nanoaod::FlatTable>("tctableextension");
}

void HGCWaferInfoTableProducer::beginRun(const edm::Run& run, const edm::EventSetup& es) {
    triggerTools_.eventSetup(es, geomToken_);
    aeInputUtil_.setGeometry(triggerTools_.getTriggerGeometry());
}

void HGCWaferInfoTableProducer::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
    edm::ParameterSetDescription desc;
    desc.add<edm::InputTag>("TCs", edm::InputTag(""));
    desc.add<edm::InputTag>("TCtruth", edm::InputTag(""));
    desc.add<edm::InputTag>("waferInfo", edm::InputTag(""));

    desc.add<unsigned>("bitsPerADC");
    desc.add<unsigned>("bitsPerNorm");
    desc.add<unsigned>("bitsPerCALQ");   
    desc.add<unsigned>("bitsPerInput");
    desc.add<bool>("useModuleFactor");
    desc.add<bool>("bitShiftNormalize");
    desc.add<bool>("useTransverseADC");
    desc.add<bool>("normByMax");

    desc.add<std::string>("name");
    desc.add<std::string>("tctablename"); 

    desc.add<int>("verbose", 0);
    descriptions.add("HGCWaferInfoTableProducer", desc);
}

void HGCWaferInfoTableProducer::produce(edm::Event& evt, const edm::EventSetup& es) {
    edm::Handle<edm::View<l1t::HGCalTriggerCell>> TCs_h;
    evt.getByToken(TCs_token_, TCs_h);
    const auto& TCs = *TCs_h;

    edm::Handle<edm::View<CaloML::HitTruthInfo>> TCtruth_h;
    evt.getByToken(TCtruth_token_, TCtruth_h);
    const auto& TCtruth = *TCtruth_h;

    edm::Handle<std::vector<CaloML::HGCWaferInfo>> waferInfo_h;
    evt.getByToken(waferinfo_token_, waferInfo_h);
    const auto& waferInfos_in = *waferInfo_h;

    std::vector<int> waferid, subdet, layer, waferU, waferV, hwType, zside, nTC;
    std::vector<float> eta, phi, x, y, z;
    std::vector<float> energy; 
    std::vector<float> simenergy; 
    std::vector<int> cluster0, cluster1, cluster2, cluster3; // indices of the top 4 associated simclusters for each wafer
    std::vector<float> frac0, frac1, frac2, frac3; // energy fraction of the top 4 associated simclusters for each wafer
    std::vector<int> sumCALQ;

    std::vector<int> norm, ADC, CALQ;
    std::vector<float> AEin;

    std::vector<int> TCidx;

    for (const auto& waferInfo : waferInfos_in) {
        if (waferInfo.TCindices.empty()) {
            printf("Warning: empty wafer. Should not happen, as waferInfo vector should be zero-suppressed. Check what went wrong!");
            continue; // Skip wafers with no TCs
        }

        waferid.push_back(waferInfo.waferID);
        nTC.push_back(waferInfo.TCindices.size());

        DetId tc0(TCs[waferInfo.TCindices[0]].detId());
    
        // wafer properties
        zside.push_back(triggerTools_.zside(tc0));
        layer.push_back(triggerTools_.layerWithOffset(tc0));

        if (tc0.det() == DetId::HGCalTrigger) {
            HGCalTriggerDetId tc0_trg(tc0);  
            subdet.push_back(tc0_trg.subdet());
            waferU.push_back(tc0_trg.waferU());
            waferV.push_back(tc0_trg.waferV());
            hwType.push_back(tc0_trg.type());
        } else if (tc0.det() == DetId::HGCalHSc) {
            HGCScintillatorDetId tc0_sci(tc0);
            subdet.push_back(tc0_sci.subdet());

            int sipmtype = tc0_sci.sipm(); //two values
            int granularity = tc0_sci.granularity(); //two values
            int tiletype = tc0_sci.type(); //four values
            
            int type = sipmtype + 2*granularity + 4*tiletype;

            hwType.push_back(type); 

            // no such thing as U/V for scintillator
            // instead do iRing/iPhi
            HGCalTriggerModuleDetId modid(waferInfo.waferID);
            waferU.push_back(modid.eta()); 
            waferV.push_back(modid.phi());
        } else {
            throw cms::Exception("InvalidDetId") << "TC detId is neither HGCalTrigger nor HGCalHSc! Check the input data.";
        }

        // position 
        auto pos = triggerTools_.getTriggerGeometry()->getModulePosition(waferInfo.waferID);
        eta.push_back(pos.eta());
        phi.push_back(pos.phi());
        x.push_back(pos.x());
        y.push_back(pos.y());
        z.push_back(pos.z());

        //total energy
        double Etot = 0;
        for (unsigned TCidx : waferInfo.TCindices) {
            Etot += TCs[TCidx].energy();
        }
        energy.push_back(Etot);

        //truth info
        double simEtot = 0;
        std::unordered_map<int, double> simcluster_energy; // simcluster index -> energy contribution to the wafer
        for (unsigned TCidx : waferInfo.TCindices){
            const auto& truth = TCtruth[TCidx];
            float Esim = truth.simenergy;
            simEtot += Esim;
            for (unsigned i=0; i<truth.simclusters.size(); ++i) {
                unsigned simcluster_idx = truth.simclusters[i];
                float frac = truth.fracs[i];
                simcluster_energy[simcluster_idx] += Esim * frac; // add the contribution from this TC to the simcluster
            }
        }

        simenergy.push_back(simEtot);
        // find the top 4 simclusters contributing to this wafer
        std::vector<std::pair<int, double>> simcluster_energy_vec(simcluster_energy.begin(), simcluster_energy.end());
        std::sort(simcluster_energy_vec.begin(), simcluster_energy_vec.end(), [](const auto& a, const auto& b) {
            return a.second > b.second; // sort in descending order of energy contribution
        });
        if (simcluster_energy_vec.size() > 0) {
            cluster0.push_back(simcluster_energy_vec[0].first);
            frac0.push_back(simcluster_energy_vec[0].second / simEtot);
        } else {
            cluster0.push_back(-1); // no associated simcluster
            frac0.push_back(0);
        }
        if (simcluster_energy_vec.size() > 1) {
            cluster1.push_back(simcluster_energy_vec[1].first);
            frac1.push_back(simcluster_energy_vec[1].second / simEtot);
        } else {
            cluster1.push_back(-1);
            frac1.push_back(0);
        }
        if (simcluster_energy_vec.size() > 2) {
            cluster2.push_back(simcluster_energy_vec[2].first);
            frac2.push_back(simcluster_energy_vec[2].second / simEtot);
        } else {
            cluster2.push_back(-1);
            frac2.push_back(0);
        }
        if (simcluster_energy_vec.size() > 3) {
            cluster3.push_back(simcluster_energy_vec[3].first);
            frac3.push_back(simcluster_energy_vec[3].second / simEtot);
        } else {
            cluster3.push_back(-1);
            frac3.push_back(0);
        }

        TCidx.insert(TCidx.end(), waferInfo.TCindices.begin(), waferInfo.TCindices.end());


        // AE input util
        

        if (tc0.det() == DetId::HGCalHSc){
            // AE input not defined for scintillator, just fill in dummy values
            sumCALQ.push_back(-1);
            for (unsigned i=0; i< nInputs_; ++i) {
                norm.push_back(-1);
                ADC.push_back(-1);
                CALQ.push_back(-1);
                AEin.push_back(-1);
            }
        } else {
            // it wants as input a vector of TCs
            std::vector<l1t::HGCalTriggerCell> TCs_in_wafer;
            for (unsigned TCidx : waferInfo.TCindices){
                TCs_in_wafer.push_back(TCs[TCidx]);
            }
            aeInputUtil_.run(TCs_in_wafer);
            sumCALQ.push_back(aeInputUtil_.getModSum());

            for (unsigned i=0; i< nInputs_; ++i) {
                norm.push_back(aeInputUtil_.getNorm(i));
                ADC.push_back(aeInputUtil_.getADC(i));
                CALQ.push_back(aeInputUtil_.getCALQ(i));
                AEin.push_back(aeInputUtil_.getInput(i)/aeInputUtil_.getInputNorm());
            }
        }

    }

    auto waferTable = std::make_unique<nanoaod::FlatTable>(waferid.size(), name_, false, false);
    waferTable->addColumn<int>("waferid", waferid, "Wafer ID");
    waferTable->addColumn<int>("nTC", nTC, "Number of TCs in the wafer");
    waferTable->addColumn<int>("subdet", subdet, "Subdetector");
    waferTable->addColumn<int>("layer", layer, "Layer");
    waferTable->addColumn<int>("waferU", waferU, "Wafer U coordinate");
    waferTable->addColumn<int>("waferV", waferV, "Wafer V coordinate");
    waferTable->addColumn<int>("hwType", hwType, "Wafer type");
    waferTable->addColumn<int>("zside", zside, "Z-side");
    waferTable->addColumn<float>("eta", eta, "Wafer eta");
    waferTable->addColumn<float>("phi", phi, "Wafer phi");
    waferTable->addColumn<float>("x", x, "Wafer x position");
    waferTable->addColumn<float>("y", y, "Wafer y position");
    waferTable->addColumn<float>("z", z, "Wafer z position");
    waferTable->addColumn<float>("energy", energy, "Total energy of TCs in the wafer");
    waferTable->addColumn<float>("simenergy", simenergy, "Total simulated energy associated with the wafer");
    waferTable->addColumn<int>("cluster0", cluster0, "Index of the most contributing simcluster");
    waferTable->addColumn<float>("frac0", frac0, "Energy fraction of the most contributing simcluster");
    waferTable->addColumn<int>("cluster1", cluster1, "Index of the 2nd most contributing simcluster");
    waferTable->addColumn<float>("frac1", frac1, "Energy fraction of the 2nd most contributing simcluster");
    waferTable->addColumn<int>("cluster2", cluster2, "Index of the 3rd most contributing simcluster");
    waferTable->addColumn<float>("frac2", frac2, "Energy fraction of the 3rd most contributing simcluster");
    waferTable->addColumn<int>("cluster3", cluster3, "Index of the 4th most contributing simcluster");
    waferTable->addColumn<float>("frac3", frac3, "Energy fraction of the 4th most contributing simcluster");
    waferTable->addColumn<int>("sumCALQ", sumCALQ, "Sum of CALQ of the TCs in the wafer");
    evt.put(std::move(waferTable), "wafers");

    auto assocTable = std::make_unique<nanoaod::FlatTable>(TCidx.size(), name_ + "TCs", false, false);
    assocTable->addColumn<int>("TCidx", TCidx, "Trigger Cell Index");
    evt.put(std::move(assocTable), "TCassociation");

    auto econTable = std::make_unique<nanoaod::FlatTable>(norm.size(), name_ + "ECONinputs", false, false);
    econTable->addColumn<int>("norm", norm, "AE input norm");
    econTable->addColumn<int>("ADC", ADC, "AE input ADC");
    econTable->addColumn<int>("CALQ", CALQ, "AE input CALQ");
    econTable->addColumn<float>("AEin", AEin, "AE input");
    evt.put(std::move(econTable), "ECONinputs");

    std::vector<int> TC_waferidx;
    for (const auto& TC : TCs) { 
        int wafer_idx = findTheWaferIndex(waferInfos_in, TC.detId());
        if (wafer_idx == -1) {
            printf("Warning: TC with detId %d does not belong to any wafer! Check the input data and the geometry.\n", TC.detId());
            TC_waferidx.push_back(-1); 
        } else {
            TC_waferidx.push_back(wafer_idx);
        }
    }

    auto tctable = std::make_unique<nanoaod::FlatTable>(TC_waferidx.size(), tctablename_, false, true);
    tctable->addColumn<int>("waferidx", TC_waferidx, "Index of the wafer this TC belongs to, -1 if not found");
    evt.put(std::move(tctable), "tctableextension");
}

DEFINE_FWK_MODULE(HGCWaferInfoTableProducer);