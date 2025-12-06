#ifndef CALOML_CALOHITS_INTERFACE_UTIL_H
#define CALOML_CALOHITS_INTERFACE_UTIL_H

namespace CaloML {
    template <typename HitType>
    uint32_t detIdFromHit(const HitType& hit){
        static_assert(sizeof(HitType) == 0, "detIdFromHit not implemented for this HitType");
        return 0;
    }

    template <>
    uint32_t detIdFromHit(const PCaloHit& hit) { 
        return hit.id();
      }
    
      template <>
      uint32_t detIdFromHit(const CaloRecHit& hit) { 
        return hit.detid();
      }
    
      template <>
      uint32_t detIdFromHit(const reco::PFRecHit& hit) { 
        return hit.detId();
      }
    
      template <>
      uint32_t detIdFromHit(const EcalRecHit& hit) { 
        return hit.detid();
      }
    
      template <>
      uint32_t detIdFromHit(const HBHERecHit& hit) { 
        return hit.detid();
      }
    
      template <>
      uint32_t detIdFromHit(const HFRecHit& hit) { 
        return hit.detid();
      }
    
      template <>
      uint32_t detIdFromHit(const HORecHit& hit) { 
        return hit.detid();
      }
};


#endif