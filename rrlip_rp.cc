/**
 * Copyright (c) 2018 Inria
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are
 * met: redistributions of source code must retain the above copyright
 * notice, this list of conditions and the following disclaimer;
 * redistributions in binary form must reproduce the above copyright
 * notice, this list of conditions and the following disclaimer in the
 * documentation and/or other materials provided with the distribution;
 * neither the name of the copyright holders nor the names of its
 * contributors may be used to endorse or promote products derived from
 * this software without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
 * "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
 * LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
 * A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
 * OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
 * SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
 * LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
 * DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
 * THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
 * (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
 * OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 *
 * Authors: Daniel Carvalho
 */

#include "mem/cache/replacement_policies/rrlip_rp.hh"

#include <cassert>
#include <memory>

#include "params/RRLIPRP.hh"

RRLIPRP::RRLIPRP(const Params *p)
    : BaseReplacementPolicy(p), threshold(p->threshold)
{
}

void
RRLIPRP::invalidate(const std::shared_ptr<ReplacementData>& replacement_data)
const
{
    // Reset last touch timestamp and reference count
    std::static_pointer_cast<RRLIPReplData>(
        replacement_data)->lastTouchTick = Tick(0);
    std::static_pointer_cast<RRLIPReplData>(
        replacement_data)->reference_count=0;
}

void
RRLIPRP::touch(const std::shared_ptr<ReplacementData>& replacement_data) const
{
    /*Update the last touch tock value based on the reference count
    if the refrence count is greater than threshold assign the current
    tick which will make the entry MRU else assign initial tick which
    will make the current entry LRU*/
    
    std::static_pointer_cast<RRLIPReplData>(
        replacement_data)->reference_count++;
    if(std::static_pointer_cast<RRLIPReplData>(
        replacement_data)->reference_count++ > 10){
        std::static_pointer_cast<RRLIPReplData>(
            replacement_data)->lastTouchTick = curTick();}
    else{
        std::static_pointer_cast<RRLIPReplData>(
            replacement_data)->lastTouchTick = Tick(0);
    }

}

void
RRLIPRP::reset(const std::shared_ptr<ReplacementData>& replacement_data) const
{
    /* When an entry is inserted set the last tick value
    to intitial value to make the newly inserted entry LRU
    also add 1 to the reference count
    */
    std::static_pointer_cast<RRLIPReplData>(
        replacement_data)->lastTouchTick = Tick(0);
    std::static_pointer_cast<RRLIPReplData>(
        replacement_data)->reference_count++;

}

ReplaceableEntry*
RRLIPRP::getVictim(const ReplacementCandidates& candidates) const
{
    // There must be at least one replacement candidate
    assert(candidates.size() > 0);

    // Visit all candidates to find victim
    ReplaceableEntry* victim = candidates[0];
    for (const auto& candidate : candidates) {
        // Update victim entry if necessary
        if (std::static_pointer_cast<RRLIPReplData>(
                    candidate->replacementData)->lastTouchTick <
                std::static_pointer_cast<RRLIPReplData>(
                    victim->replacementData)->lastTouchTick ) {
            victim = candidate;
        }
    }

    return victim;
}

std::shared_ptr<ReplacementData>
RRLIPRP::instantiateEntry()
{
    return std::shared_ptr<ReplacementData>(new RRLIPReplData());
}

RRLIPRP*
RRLIPRPParams::create()
{
    return new RRLIPRP(this);
}