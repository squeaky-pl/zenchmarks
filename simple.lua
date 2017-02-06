init = function(args)
   local r = {}
   r[1] = wrk.format(nil, "/?q=a")
   r[2] = wrk.format(nil, "/?")
   r[3] = wrk.format(nil, "/?q=A")
   r[4] = wrk.format(nil, "/?q=b")
   r[5] = wrk.format(nil, "/?q=D")
   r[6] = wrk.format(nil, "/?")
   r[7] = wrk.format(nil, "/")
   r[8] = wrk.format(nil, "/?q=h")
   r[9] = wrk.format(nil, "/?q=J")
   r[10] = wrk.format(nil, "/?q=q")
   r[11] = wrk.format(nil, "/?q=R")
   r[12] = wrk.format(nil, "/?q=O")
   r[13] = wrk.format(nil, "/?q=X")
   r[14] = wrk.format(nil, "/?")
   r[15] = wrk.format(nil, "/?q=x")
   r[16] = wrk.format(nil, "/?q=P")
   r[17] = wrk.format(nil, "/?q=c")
   r[18] = wrk.format(nil, "/?")
   r[19] = wrk.format(nil, "/")
   r[20] = wrk.format(nil, "/?q=M")
   r[21] = wrk.format(nil, "/?q=s")
   r[22] = wrk.format(nil, "/?q=K")
   r[23] = wrk.format(nil, "/?q=z")
   r[24] = wrk.format(nil, "/?q=Z")

   req = table.concat(r)
end

request = function()
   return req
end
